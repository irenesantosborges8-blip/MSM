#!/usr/bin/env python3
import os
import sys
import json
import time
import random
import hmac
import hashlib
import sqlite3
import uuid

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

try:
    from Crypto.Cipher import AES
except ImportError:
    try:
        from Cryptodome.Cipher import AES
    except ImportError:
        AES = None

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "server-data", "msm_server.db")
ENCRYPTION_VECTOR = b"zq3zn4dx2h3k4im6"
ENCRYPTION_KEY = b"y26ju5h9r28eh3h2"
HOST = "0.0.0.0"
PORT = int(os.environ.get("AUTH_PORT", "8080"))

def pad(data):
    bs = 16
    return data + (bs - len(data) % bs) * chr(bs - len(data) % bs)

def encrypt_aes_cfb8(plaintext, key, iv):
    if AES is not None:
        try:
            key_bytes = key[:16].ljust(16, b'\0')
            iv_bytes = iv[:16].ljust(16, b'\0')
            cipher = AES.new(key_bytes, AES.MODE_CFB, iv_bytes, segment_size=8)
            return cipher.encrypt(plaintext.encode("utf-8"))
        except Exception:
            pass
    from Crypto.Cipher import AES as AES2
    key_bytes = key[:16].ljust(16, b'\0')
    iv_bytes = iv[:16].ljust(16, b'\0')
    cipher = AES2.new(key_bytes, AES2.MODE_CFB, iv_bytes, segment_size=8)
    return cipher.encrypt(plaintext.encode("utf-8"))

import base64

class AuthHandler(BaseHTTPRequestHandler):
    def get_db(self):
        return sqlite3.connect(DB_PATH)

    def generate_bbb_id(self):
        return random.randint(100000000, 999999999)

    def generate_user_game_id(self):
        return str(uuid.uuid4())

    def generate_token(self, bbb_id, user_game_id, username, login_type, ip):
        payload = {
            "user_game_ids": [user_game_id],
            "username": username,
            "login_type": login_type,
            "bbb_id": bbb_id,
            "ip_address": ip,
            "server_location": "private",
            "can_play": True,
            "cant_play_reason": " "
        }
        plaintext = json.dumps(payload, separators=(',', ':'))
        encrypted = encrypt_aes_cfb8(plaintext, ENCRYPTION_KEY, ENCRYPTION_VECTOR)
        return base64.b64encode(encrypted).decode("utf-8")

    def find_or_create_user(self, username, login_type, ip):
        conn = self.get_db()
        cur = conn.cursor()

        cur.execute("SELECT bbb_id, user_game_id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

        if row:
            bbb_id, user_game_id = row
        else:
            bbb_id = self.generate_bbb_id()
            user_game_id = self.generate_user_game_id()
            now = int(time.time())
            cur.execute(
                "INSERT INTO users (bbb_id, user_game_id, username, login_type, date_created) VALUES (?, ?, ?, ?, ?)",
                (bbb_id, user_game_id, username, login_type, now)
            )
            cur.execute(
                "INSERT OR IGNORE INTO players (id, display_name, date_created) VALUES (?, ?, ?)",
                (user_game_id, username, now)
            )
            conn.commit()

        conn.close()
        return bbb_id, user_game_id

    def do_GET(self):
        if self.path.startswith("/auth"):
            query = {}
            if "?" in self.path:
                qs = self.path.split("?", 1)[1]
                for part in qs.split("&"):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        query[k] = v

            username = query.get("u", "anon")
            login_type = query.get("t", "anon")
            ip = self.client_address[0]

            bbb_id, user_game_id = self.find_or_create_user(username, login_type, ip)
            token = self.generate_token(bbb_id, user_game_id, username, login_type, ip)

            resp = {
                "ok": True,
                "access_token": token,
                "user_game_id": [user_game_id],
                "message": "Authenticated"
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"MSM Private Auth Server - Use GET /auth?u=username&t=anon")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""

        if "/auth/api/token" in self.path:
            query = {}
            if "?" in self.path:
                qs = self.path.split("?", 1)[1]
                for part in qs.split("&"):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        query[k] = v

            username = query.get("u", "anon")
            password = query.get("p", "any")
            login_type = query.get("t", "anon")
            ip = self.client_address[0]

            bbb_id, user_game_id = self.find_or_create_user(username, login_type, ip)
            token = self.generate_token(bbb_id, user_game_id, username, login_type, ip)

            resp = {
                "ok": True,
                "access_token": token,
                "user_game_id": [user_game_id],
                "message": "Authenticated"
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        elif "/pregame_setup" in self.path:
            resp = {
                "ok": True,
                "serverIp": "127.0.0.1",
                "contentUrl": "http://127.0.0.1:8082/content",
                "serverPort": 9933,
                "message": "Pregame setup complete"
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "message": "Not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[AUTH] {args[0]} {args[1]} {args[2]}")

def main():
    if AES is None:
        print("WARNING: PyCryptodome not installed, trying fallback...")
        print("Install with: pip install pycryptodome")

    server = HTTPServer((HOST, PORT), AuthHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f"Auth server running on http://{HOST}:{PORT}")
    print(f"Token endpoint: GET http://{HOST}:{PORT}/auth?u=username")
    print(f"Token endpoint: POST http://{HOST}:{PORT}/auth/api/token/?u=username&p=pass&t=anon")
    print(f"Pregame setup: POST http://{HOST}:{PORT}/pregame_setup")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()

if __name__ == "__main__":
    main()
