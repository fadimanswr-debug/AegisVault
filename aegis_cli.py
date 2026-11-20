#!/usr/bin/env python3
import argparse
import getpass
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

CONFIG_PATH = Path.home() / ".aegisrc"
DEFAULT_SERVER = "http://192.168.50.1:5000"

C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

BANNER = r"""
    ___    ___________________________    _____    __  ____  ______
   /   |  / ____/ ____/  _/ ___/__  /   / /   |  / / / / / /_  __/
  / /| | / __/ / / __ / / \__ \  / /   / / /| | / / / / /    / /   
 / ___ |/ /___/ /_/ // / ___/ / / /___/ / ___ |/ /_/ / /___ / /    
/_/  |_/_____/\____/___//____/ /_____/_/  |_|\____/_____//_/     
"""


def splash_screen(server_url: str) -> None:
    if not sys.stdout.isatty():
        return
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.write(f"{C_CYAN}{C_BOLD}{BANNER}{C_RESET}\n")
    sys.stdout.write(f"  {C_YELLOW}[*] AegisVault Security Suite v2.0  |  Target: {server_url}{C_RESET}\n\n")
    sys.stdout.flush()

    stages = [
        "Initializing crypto engine (PBKDF2 + HMAC)",
        "Verifying distributed transport channel",
        "Syncing audit telemetry & vault state",
    ]
    spinner = ["|", "/", "-", "\\"]

    for stage in stages:
        for i in range(6):
            ch = spinner[i % len(spinner)]
            sys.stdout.write(f"\r  {C_CYAN}[{ch}]{C_RESET} {stage}...")
            sys.stdout.flush()
            time.sleep(0.045)
        sys.stdout.write(f"\r  {C_GREEN}[OK]{C_RESET} {stage}        \n")
        sys.stdout.flush()
    time.sleep(0.12)


def load_server_url() -> str:
    if CONFIG_PATH.exists():
        val = CONFIG_PATH.read_text(encoding="utf-8").strip()
        if val:
            return val.rstrip("/")
    return DEFAULT_SERVER


def save_server_url(url: str) -> None:
    CONFIG_PATH.write_text(url.strip().rstrip("/") + "\n", encoding="utf-8")


def api_call(method: str, base_url: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    url = f"{base_url.rstrip('/')}{path}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}
    except Exception as e:
        return 0, {"error": str(e)}


def print_result(code: int, res: dict) -> None:
    color = C_GREEN if 200 <= code < 300 else C_RED
    print(f"\n{color}{C_BOLD}[HTTP {code}]{C_RESET}")
    print(json.dumps(res, indent=2, ensure_ascii=False))


def interactive_shell(base_url: str) -> None:
    while True:
        print(f"\n{C_CYAN}{C_BOLD}=== AegisVault Interactive Console ==={C_RESET}")
        print("  1) Store secret   (تشفير وحفظ)")
        print("  2) Read secret    (قراءة وفك تشفير)")
        print("  3) List entries   (عرض السجلات)")
        print("  4) Delete entry   (حذف سجل)")
        print("  5) Audit log      (سجل التدقيق)")
        print("  6) Server status  (حالة الخادم)")
        print("  0) Exit           (خروج)")
        choice = input(f"{C_YELLOW}aegis> {C_RESET}").strip()

        if choice == "1":
            label = input("Label: ").strip() or "note"
            secret = input("Secret: ").strip()
            pw = getpass.getpass("Passphrase (hidden): ").strip()
            code, res = api_call("POST", base_url, "/store", {"label": label, "secret": secret, "passphrase": pw})
            print_result(code, res)
        elif choice == "2":
            entry_id = input("Entry ID: ").strip()
            pw = getpass.getpass("Passphrase (hidden): ").strip()
            if entry_id.isdigit():
                code, res = api_call("POST", base_url, "/read", {"id": int(entry_id), "passphrase": pw})
                print_result(code, res)
            else:
                print(f"{C_RED}[!] ID must be a number.{C_RESET}")
        elif choice == "3":
            code, res = api_call("GET", base_url, "/entries")
            print_result(code, res)
        elif choice == "4":
            entry_id = input("Entry ID to delete: ").strip()
            if entry_id.isdigit():
                code, res = api_call("DELETE", base_url, f"/entries/{int(entry_id)}")
                print_result(code, res)
            else:
                print(f"{C_RED}[!] ID must be a number.{C_RESET}")
        elif choice == "5":
            code, res = api_call("GET", base_url, "/audit")
            print_result(code, res)
        elif choice == "6":
            code, res = api_call("GET", base_url, "/status")
            print_result(code, res)
        elif choice == "0":
            print(f"{C_CYAN}Session closed.{C_RESET}")
            break
        else:
            print(f"{C_RED}[!] Invalid option.{C_RESET}")


def main() -> None:
    base_url = load_server_url()

    parser = argparse.ArgumentParser(prog="aegis", description="AegisVault CLI")
    parser.add_argument("--server", default=base_url, help="Override server URL")
    parser.add_argument("--no-anim", action="store_true", help="Skip startup animation")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("shell", help="Interactive menu")
    sub.add_parser("status", help="Server status")
    sub.add_parser("ls", help="List stored entries")
    sub.add_parser("logs", help="Show audit log")

    p_cfg = sub.add_parser("config", help="Set default server URL")
    p_cfg.add_argument("url", help="Example: http://192.168.50.1:5000")

    p_add = sub.add_parser("add", help="Encrypt & store secret")
    p_add.add_argument("label", help="Record label")
    p_add.add_argument("secret", help="Secret text")
    p_add.add_argument("-p", "--passphrase", help="Passphrase (prompted if omitted)")

    p_get = sub.add_parser("get", help="Read & decrypt secret by ID")
    p_get.add_argument("id", type=int, help="Record ID")
    p_get.add_argument("-p", "--passphrase", help="Passphrase (prompted if omitted)")

    p_del = sub.add_parser("del", help="Delete entry by ID")
    p_del.add_argument("id", type=int, help="Record ID")

    args = parser.parse_args()
    srv = args.server.rstrip("/")

    if not args.no_anim:
        splash_screen(srv)

    if args.cmd is None or args.cmd == "shell":
        interactive_shell(srv)
        return

    if args.cmd == "config":
        save_server_url(args.url)
        print(f"{C_GREEN}[OK]{C_RESET} Saved server URL: {args.url}")
        return

    if args.cmd == "status":
        code, res = api_call("GET", srv, "/status")
    elif args.cmd == "ls":
        code, res = api_call("GET", srv, "/entries")
    elif args.cmd == "logs":
        code, res = api_call("GET", srv, "/audit")
    elif args.cmd == "add":
        pw = args.passphrase or getpass.getpass("Passphrase: ").strip()
        code, res = api_call("POST", srv, "/store", {"label": args.label, "secret": args.secret, "passphrase": pw})
    elif args.cmd == "get":
        pw = args.passphrase or getpass.getpass("Passphrase: ").strip()
        code, res = api_call("POST", srv, "/read", {"id": args.id, "passphrase": pw})
    elif args.cmd == "del":
        code, res = api_call("DELETE", srv, f"/entries/{args.id}")
    else:
        parser.print_help()
        sys.exit(1)

    print_result(code, res)


if __name__ == "__main__":
    main()
