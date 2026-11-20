# AegisVault v2

A distributed encrypted vault system with a Python ThreadingHTTPServer backend, SQLite storage + audit logging, a web dashboard, and an interactive CLI (aegis) for Kali Linux.

## Features
- Cryptography: PBKDF2-HMAC-SHA256 key derivation with per-entry random salt and HMAC-SHA256 integrity verification.
- Database & Audit Log: SQLite storage (vault_entries) with operation tracking (audit_log).
- Web Dashboard: Browser interface on port 5000 for storing, decrypting, listing, deleting entries, and viewing audit logs.
- Kali CLI (aegis): ASCII splash animation, interactive console mode, server URL config (~/.aegisrc), and quick commands.

## Quick Install on Kali Linux
curl -fsSL [https://raw.githubusercontent.com/fadimanswr-debug/AegisVault/main/install.sh](https://raw.githubusercontent.com/fadimanswr-debug/AegisVault/main/install.sh) | bash -s "[http://192.168.50.1:5000](http://192.168.50.1:5000)"

## CLI Usage
- aegis                 # Interactive console
- aegis ls              # List entries
- aegis add label text  # Encrypt & store secret
- aegis get <id>        # Decrypt secret by ID
- aegis del <id>        # Delete entry by ID
- aegis logs            # View audit log
- aegis status          # Check server status
