#!/bin/bash
set -e

echo "=== MSM Private Server Setup ==="
echo ""

# Config
SFS2X_VERSION="2.19.0"
SFS2X_URL="https://www.smartfoxserver.com/download/sfs2x"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
SERVER_DATA_DIR="$PROJECT_DIR/server-data"
AUTH_DIR="$PROJECT_DIR/auth-server"

echo "[1/5] Creating directory structure..."
mkdir -p "$SERVER_DATA_DIR/json_db"
mkdir -p "$SERVER_DATA_DIR/player_data"
mkdir -p "$SERVER_DATA_DIR/game_data"
mkdir -p "$PROJECT_DIR/sfs2x"
echo "  OK"

echo "[2/5] Initializing database..."
python3 "$PROJECT_DIR/init_db.py"
cp "$SERVER_DATA_DIR/msm_server.db" "$SERVER_DATA_DIR/json_db/game_data.db"
echo "  OK"

echo "[3/5] Setting up auth server..."
cd "$AUTH_DIR"
pip install -q pycryptodome 2>/dev/null || true
echo "  OK"

echo "[4/5] Extracting game data for static serving..."
python3 "$PROJECT_DIR/export_game_data.py" 2>/dev/null || echo "  WARNING: export script not found, skipping"
echo "  OK"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Download SmartFoxServer 2X Community Edition:"
echo "     Visit: https://www.smartfoxserver.com/download/sfs2x"
echo "     Download: Linux/Unix x86_64 installer"
echo "     Run: sudo bash SFS2X_*.sh"
echo ""
echo "  2. Start the auth server:"
echo "     cd $AUTH_DIR && python3 auth_server.py &"
echo ""
echo "  3. Deploy the extension to SFS2X:"
echo "     cp misc/mainExtension.jar /path/to/SFS2X/extensions/MSMSandbox/"
echo "     cp -r server-data /path/to/SFS2X/"
echo "     Configure SFS2X AdminTool -> Zone -> Add Extension"
echo ""
echo "  4. Start SmartFoxServer:"
echo "     cd /path/to/SFS2X && ./sfs2x-service start"
echo ""
echo "  5. Patch your MSM client to connect to your server"
echo ""
