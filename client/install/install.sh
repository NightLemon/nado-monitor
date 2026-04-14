#!/usr/bin/env bash
# Nado Monitor — Telemetry Client Installer (Linux / WSL / macOS)
#
# One-line install:
#   curl -fsSL https://raw.githubusercontent.com/NightLemon/nado-monitor/main/client/install/install.sh | bash -s -- --key YOUR_API_KEY
#
# Options:
#   --key KEY         API key for the server (required, or set NADO_API_KEY env)
#   --server URL      Server URL (default: https://nado-monitor.azurewebsites.net)
#   --upgrade         Upgrade existing installation
#   --uninstall       Remove the client and service
#
set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
REPO_URL="https://github.com/NightLemon/nado-monitor.git"
INSTALL_DIR="/opt/nado-monitor"
SERVER_URL="https://nado-monitor.azurewebsites.net"
SERVICE_NAME="nado-telemetry"
PIP_SPEC="nado-telemetry @ git+${REPO_URL}#subdirectory=client"
API_KEY="${NADO_API_KEY:-}"
UPGRADE=false
UNINSTALL=false

# ── Parse arguments ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --key)      API_KEY="$2";     shift 2 ;;
    --server)   SERVER_URL="$2";  shift 2 ;;
    --upgrade)  UPGRADE=true;     shift   ;;
    --uninstall) UNINSTALL=true;  shift   ;;
    *) echo "Unknown option: $1"; exit 1  ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────
as_root() {
  if [ "$(id -u)" -eq 0 ]; then
    "$@"
  elif command -v sudo &>/dev/null; then
    sudo "$@"
  else
    echo "Error: need root. Run as root or install sudo." >&2
    exit 1
  fi
}

# ── Uninstall ─────────────────────────────────────────────────────────────────
if $UNINSTALL; then
  echo "==> Uninstalling ${SERVICE_NAME}..."
  as_root systemctl stop ${SERVICE_NAME} 2>/dev/null || true
  as_root systemctl disable ${SERVICE_NAME} 2>/dev/null || true
  as_root rm -f /etc/systemd/system/${SERVICE_NAME}.service
  as_root systemctl daemon-reload
  rm -rf "${INSTALL_DIR}"
  echo "==> Removed."
  exit 0
fi

# ── Validate ──────────────────────────────────────────────────────────────────
if [ -z "$API_KEY" ]; then
  echo "Error: API key required. Use --key YOUR_KEY or set NADO_API_KEY."
  exit 1
fi

# Check python3
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 not found. Install python3 first."
  exit 1
fi

# Check python3 venv support
if ! python3 -m venv --help &>/dev/null 2>&1; then
  echo "Error: python3-venv not installed."
  echo "  Ubuntu/Debian: sudo apt install python3-venv"
  echo "  Fedora/RHEL:   sudo dnf install python3"
  exit 1
fi

# ── Install ───────────────────────────────────────────────────────────────────
echo "==> Installing nado-telemetry client..."

as_root mkdir -p "$INSTALL_DIR"
as_root chown "$(whoami)" "$INSTALL_DIR"

# Venv
if [ ! -d "$INSTALL_DIR/venv" ]; then
  echo "  Creating Python venv..."
  python3 -m venv "$INSTALL_DIR/venv"
fi
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q 2>/dev/null

# Install/upgrade package
if $UPGRADE; then
  echo "  Upgrading package..."
  "$INSTALL_DIR/venv/bin/pip" install --upgrade "$PIP_SPEC" -q
else
  echo "  Installing package..."
  "$INSTALL_DIR/venv/bin/pip" install "$PIP_SPEC" -q
fi

# Verify
if ! "$INSTALL_DIR/venv/bin/nado-telemetry" --help &>/dev/null; then
  echo "Error: nado-telemetry not found after install."
  exit 1
fi
echo "  Installed successfully."

# ── Systemd service ──────────────────────────────────────────────────────────
echo "==> Configuring systemd service..."
as_root tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<UNIT
[Unit]
Description=Nado Monitor Telemetry Client
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(whoami)
ExecStart=${INSTALL_DIR}/venv/bin/nado-telemetry
Restart=always
RestartSec=10
Environment=NADO_SERVER_URL=${SERVER_URL}
Environment=NADO_API_KEY=${API_KEY}

[Install]
WantedBy=multi-user.target
UNIT

as_root systemctl daemon-reload
as_root systemctl enable ${SERVICE_NAME}
as_root systemctl restart ${SERVICE_NAME}

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "==> Done! Service is running."
sleep 1
as_root systemctl status ${SERVICE_NAME} --no-pager -l 2>/dev/null | head -8 || true
echo ""
echo "Commands:"
echo "  systemctl status ${SERVICE_NAME}           # check status"
echo "  journalctl -u ${SERVICE_NAME} -f           # view logs"
echo "  systemctl restart ${SERVICE_NAME}           # restart"
echo "  bash <(curl -fsSL ...) --upgrade --key KEY  # upgrade"
echo "  bash <(curl -fsSL ...) --uninstall          # remove"
