#!/bin/bash
# MSM Private Server Management Script
set -e

SFS2X_DIR="/workspaces/MSM/msm-server/sfs2x/SFS2X"
AUTH_DIR="/workspaces/MSM/msm-server/auth-server"
DB_DIR="/home/ubuntu/MSMSandbox/ServerData/json_db"

start_sfs2x() {
    echo "Starting SFS2X..."
    cd "$SFS2X_DIR"
    setsid ./sfs2x.sh &>/tmp/sfs2x_out.log &
    echo "SFS2X PID: $!"
    sleep 5
    if pgrep -f "com.smartfoxserver.v2.Main" > /dev/null; then
        echo "SFS2X is running!"
        tail -3 logs/smartfox.log 2>/dev/null | grep -o "READY\|Error" || true
    else
        echo "SFS2X failed to start - check /tmp/sfs2x_out.log"
    fi
}

start_auth() {
    echo "Starting Auth Server..."
    AUTH_PORT=${AUTH_PORT:-8082}
    cd "$AUTH_DIR"
    # Kill old instance
    pkill -f "auth_server.py" 2>/dev/null || true
    sleep 1
    nohup python3 auth_server.py &>/tmp/auth_server.log &
    echo "Auth PID: $!"
    sleep 2
    if curl -s "http://127.0.0.1:$AUTH_PORT/auth" > /dev/null 2>&1; then
        echo "Auth server running on port $AUTH_PORT"
    else
        echo "Auth server may have failed - check /tmp/auth_server.log"
    fi
}

stop() {
    echo "Stopping all services..."
    pkill -f "com.smartfoxserver.v2.Main" 2>/dev/null || true
    pkill -f "auth_server.py" 2>/dev/null || true
    echo "Stopped."
}

status() {
    echo "=== Service Status ==="
    if pgrep -f "com.smartfoxserver.v2.Main" > /dev/null; then
        echo "SFS2X: RUNNING"
        ps aux | grep "v2.Main" | grep -v grep | awk '{print "  PID: "$2"  Uptime: "$9}'
    else
        echo "SFS2X: STOPPED"
    fi
    
    if pgrep -f "auth_server.py" > /dev/null; then
        echo "Auth: RUNNING"
    else
        echo "Auth: STOPPED"
    fi
    
    echo "=== Port Status ==="
    ss -tlnp | grep -E "9933|808[0-9]" || echo "  (none)"
}

rebuild() {
    echo "Rebuilding extension..."
    cd /workspaces/MSM/msm-server
    bash build_extension.sh
}

case "${1:-help}" in
    start)
        start_sfs2x
        start_auth
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start_sfs2x
        start_auth
        ;;
    status)
        status
        ;;
    rebuild)
        rebuild
        ;;
    logs)
        tail -f "$SFS2X_DIR/logs/smartfox.log" 2>/dev/null || echo "No logs"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|rebuild|logs}"
        echo ""
        echo "  start   - Start SFS2X and Auth server"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  status  - Show service status"
        echo "  rebuild - Recompile extension from source"
        echo "  logs    - Tail SFS2X logs"
        ;;
esac
