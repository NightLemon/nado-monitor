#!/usr/bin/env bash
# One-line install: curl this script and pipe to bash, or run directly in WSL
# Usage: bash install-wsl.sh
set -euo pipefail

REPO_URL="https://github.com/NightLemon/nado-monitor.git"
INSTALL_DIR="/opt/nado-monitor"
SERVER_URL="https://nado-monitor.azurewebsites.net"
SERVICE_NAME="nado-telemetry"
PIP_SPEC="nado-telemetry @ git+${REPO_URL}#subdirectory=client"

echo "==> Installing nado-telemetry client..."

# 1. Create install directory
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$(whoami)" "$INSTALL_DIR"

# 2. Create venv and install directly from GitHub (no git clone needed)
echo "==> Setting up Python venv..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q

if [ "${1:-}" = "--upgrade" ]; then
    echo "==> Upgrading nado-telemetry..."
    "$INSTALL_DIR/venv/bin/pip" install --upgrade "$PIP_SPEC" -q
else
    echo "==> Installing nado-telemetry..."
    "$INSTALL_DIR/venv/bin/pip" install "$PIP_SPEC" -q
fi
echo "==> Installed: $("$INSTALL_DIR/venv/bin/nado-telemetry" --help 2>&1 | head -1)"

# 3. Prompt for API key if not set
if [ -z "${NADO_API_KEY:-}" ]; then
    read -rp "Enter API key: " NADO_API_KEY
fi

# 4. Create systemd service
echo "==> Creating systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<UNIT
[Unit]
Description=Nado Monitor Telemetry Client
After=network.target

[Service]
Type=simple
User=$(whoami)
ExecStart=${INSTALL_DIR}/venv/bin/nado-telemetry
Restart=always
RestartSec=10
Environment=NADO_SERVER_URL=${SERVER_URL}
Environment=NADO_API_KEY=${NADO_API_KEY}

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}

echo ""
echo "==> Done! Service status:"
sudo systemctl status ${SERVICE_NAME} --no-pager -l | head -10
echo ""
echo "Commands:"
echo "  sudo systemctl status ${SERVICE_NAME}   # check status"
echo "  sudo journalctl -u ${SERVICE_NAME} -f   # view logs"
echo "  sudo systemctl restart ${SERVICE_NAME}   # restart"
echo "  bash $0 --upgrade                        # upgrade to latest"
