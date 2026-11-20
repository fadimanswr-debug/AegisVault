#!/usr/bin/env bash
set -e

REPO_RAW_URL="https://raw.githubusercontent.com/<YOUR_USERNAME>/AegisVault/main/aegis_cli.py"
DEFAULT_SERVER="${1:-http://192.168.50.1:5000}"

echo "[*] Installing AegisVault CLI (aegis)..."
curl -fsSL "$REPO_RAW_URL" -o "$HOME/aegis_cli.py"
chmod +x "$HOME/aegis_cli.py"
sudo ln -sf "$HOME/aegis_cli.py" /usr/local/bin/aegis

echo "$DEFAULT_SERVER" > "$HOME/.aegisrc"
echo "[OK] Installed! Run 'aegis' to start."
