from pathlib import Path

# Written by StormTheory
# https://github.com/stormtheory/packhowl

# ─── Silent Link Configuration ────────────────────────────────────────────────
APP_NAME        = "Pack Howl"
APP_ICON_PATH   = "assets/wolf_red_bg.png"         # 🔔 Used by client tray

# ─── Networking ───────────────────────────────────────────────────────────────
SERVER_PORT     = 50443
SERVER_BIND     = "0.0.0.0"                 # Server binds to all interfaces
CLIENT_IP       = "0.0.0.0"                 # Client binds to all interfaces (can be overridden)

# ─── Files and Directories ────────────────────────────────────────────────────
DATA_DIR        = Path.home() / ".packhowl/"
SETTINGS_FILE   = DATA_DIR / "settings.json"
LOG_DIR         = DATA_DIR / "logs"

CERTS_DIR       = DATA_DIR / "certs"
SSL_CA_PATH     = CERTS_DIR / "ca.pem"       # 🔐 shared CA root
SSL_CERT_PATH   = CERTS_DIR / "server.pem"   # Server-side certs
CN_WHITELIST_PATH = CERTS_DIR / "cn_whitelist.txt"

# ─── System Limits ────────────────────────────────────────────────────────────
MAX_USERS       = 15

# ─── Server Security ─────────────────────────────────────────────────────────────────
SERVER_IP_BLOCK_DURATION = 300  # seconds (300 = 5 minutes block)

# ── Small helpers ─────────────────────────────────────────────────────────
def ensure_data_dirs() -> None:
    """Create ~/.packhowl & ~/.packhowl/logs on first run."""
    for d in (DATA_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)
