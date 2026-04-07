# Nado Monitor

A lightweight monitoring system for tracking cloud machine status, system metrics, and agent/tool activity (Claude Code, Node, etc.).

## Architecture

```
[Dev Box (Win)]  ──POST /api/telemetry──>  [FastAPI Server]  <──GET /api/*──  [React Dashboard]
[OpenClaw (WSL)] ──POST /api/telemetry──>       │
                                           [SQLite DB]
```

- **Telemetry Client** — Python package (`nado-telemetry`) that collects CPU/memory/disk metrics and detects running processes, posts to server every 30s
- **Server** — FastAPI app that stores telemetry in SQLite (WAL mode) and serves the dashboard API
- **Dashboard** — React SPA showing machine status cards, metric gauges, process indicators, and historical charts

## Quick Start

### 1. Start the Server

```bash
cd server
pip install -r requirements.txt
cp .env.example .env  # edit API_KEY
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Dashboard (development)

```bash
cd dashboard
npm install
npm run dev
```

Open http://localhost:5173

### 3. Run Telemetry Client on each machine

```bash
cd client
pip install .                              # installs nado-telemetry package
cp config.example.toml config.toml         # edit server_url and api_key
nado-telemetry -c config.toml              # run with config file
```

Or via environment variables (useful for containers):

```bash
pip install ./client
NADO_SERVER_URL=http://your-server:8000 \
NADO_API_KEY=your-secret-key \
nado-telemetry
```

## Docker Deployment

```bash
# Set your API key
export API_KEY=your-secret-key

# Build and run
docker-compose up -d

# Server + dashboard available at http://localhost:8000
```

## Install Client as Service

### Linux (systemd)

```bash
# Create venv and install
python3 -m venv /opt/nado-monitor/venv
/opt/nado-monitor/venv/bin/pip install /path/to/client

# Copy config
cp client/config.example.toml /opt/nado-monitor/client/config.toml
# Edit config.toml: set server_url and api_key

# Install and start service
sudo cp client/install/nado-telemetry.service /etc/systemd/system/
sudo systemctl enable --now nado-telemetry
```

### Windows (Scheduled Task)

```powershell
# Run as Administrator
cd client\install
.\install-windows.ps1 -ConfigPath "C:\path\to\config.toml"
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/telemetry` | X-API-Key | Ingest telemetry from clients |
| GET | `/api/machines` | -- | List all machines with latest metrics |
| GET | `/api/machines/{id}` | -- | Single machine detail |
| GET | `/api/machines/{id}/history?hours=24` | -- | Historical data for charts |
| GET | `/api/health` | -- | Health check |

## Configuration

### Server (.env)
- `API_KEY` -- shared secret for telemetry clients
- `DATABASE_URL` -- SQLite path (default: `sqlite:///./nado_monitor.db`)
- `HEARTBEAT_TIMEOUT_SECONDS` -- machine offline threshold (default: 90)
- `RETENTION_DAYS` -- telemetry data retention (default: 7)

### Client (config.toml or env vars)
| Config Key | Env Var | Default | Description |
|-----------|---------|---------|-------------|
| `server_url` | `NADO_SERVER_URL` | `http://localhost:8000` | Server endpoint |
| `api_key` | `NADO_API_KEY` | — | Must match server's API_KEY |
| `machine_name` | `NADO_MACHINE_NAME` | hostname | Machine identifier |
| `interval_seconds` | `NADO_INTERVAL` | 30 | Collection interval |
| `monitored_processes` | `NADO_MONITORED_PROCESSES` | claude,node,python,code,cursor,docker | Comma-separated process names |
