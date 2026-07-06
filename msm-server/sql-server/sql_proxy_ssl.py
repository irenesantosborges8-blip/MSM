import http.server
import json
import sqlite3
import os
import re
import ssl
import subprocess
import tempfile

DB_PATH = os.environ.get("MSM_DB_PATH", "/home/ubuntu/MSMSandbox/ServerData/json_db/game_data.db")
PORT = int(os.environ.get("SQL_PROXY_PORT", "443"))

MYSQL_TO_SQLITE = [
    (re.compile(r"\bIFNULL\s*\(", re.IGNORECASE), "IFNULL("),
    (re.compile(r"\bRAND\s*\(\s*\)", re.IGNORECASE), "RANDOM()"),
    (re.compile(r"`([^`]+)`"), r'"\1"'),
]

def translate_mysql_to_sqlite(sql):
    for pattern, replacement in MYSQL_TO_SQLITE:
        sql = pattern.sub(replacement, sql)
    return sql

def execute_and_fetch(sql, conn):
    cursor = conn.cursor()
    cursor.execute(sql)
    if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("WITH"):
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        result_rows = []
        for row in rows:
            str_row = []
            for val in row:
                if val is None:
                    str_row.append(None)
                elif isinstance(val, (int, float)):
                    str_row.append(val)
                else:
                    str_row.append(str(val))
            result_rows.append(str_row)
        conn.commit()
        return {"success": True, "result": result_rows, "columns": columns}
    else:
        conn.commit()
        return {"success": True, "affected": cursor.rowcount}

class SQLProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        if "/admin/exec_sql" in self.path:
            result = self.handle_exec_sql(body)
        else:
            result = json.dumps({"success": False, "error": "unknown_endpoint"})

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(result.encode("utf-8"))

    def handle_exec_sql(self, body_str):
        try:
            data = json.loads(body_str)
            sql_command = data.get("sql_command", "")
            translated = translate_mysql_to_sqlite(sql_command)
            conn = sqlite3.connect(DB_PATH)
            try:
                result = execute_and_fetch(translated, conn)
            finally:
                conn.close()
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    def log_message(self, format, *args):
        print(f"[SQL-PROXY] {args[0]} {args[1]} {args[2]}")

def generate_self_signed_cert(cert_path, key_path, hostname="riotlove.pythonanywhere.com"):
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", key_path, "-out", cert_path,
            "-days", "3650", "-nodes",
            "-subj", f"/CN={hostname}",
            "-addext", f"subjectAltName=DNS:{hostname},DNS:riotlove.pythonanywhere.com,IP:127.0.0.1"
        ], check=True, capture_output=True)
        os.chmod(cert_path, 0o644)
        os.chmod(key_path, 0o644)
        print(f"Generated self-signed cert for {hostname}")

if __name__ == "__main__":
    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    os.makedirs(cert_dir, exist_ok=True)
    cert_path = os.path.join(cert_dir, "riotlove.pythonanywhere.com.crt")
    key_path = os.path.join(cert_dir, "riotlove.pythonanywhere.com.key")

    generate_self_signed_cert(cert_path, key_path)

    if os.geteuid() != 0 and PORT < 1024:
        print(f"WARNING: Port {PORT} requires root. Using port 8443 instead.")
        PORT = 8443

    server = http.server.HTTPServer(("0.0.0.0", PORT), SQLProxyHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_path, key_path)
    server.socket = context.wrap_socket(server.socket, server_side=True)

    print(f"SQL Proxy (HTTPS) running on port {PORT}")
    print(f"DB: {DB_PATH}")
    server.serve_forever()
