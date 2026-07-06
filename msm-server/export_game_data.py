#!/usr/bin/env python3
import sqlite3
import json
import os
import sys

DB_PATH = "server-data/msm_server.db"
OUTPUT_DIR = "server-data/game_data"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

os.makedirs(OUTPUT_DIR, exist_ok=True)

def json_serialize(val):
    if val is None:
        return None
    if isinstance(val, bytes):
        return None
    return val

def export_table(table, filename=None):
    if filename is None:
        filename = f"{table}.json"
    path = os.path.join(OUTPUT_DIR, filename)
    cur.execute(f"SELECT * FROM [{table}]")
    rows = cur.fetchall()
    data = []
    for row in rows:
        d = {k: json_serialize(v) for k, v in dict(row).items()}
        data.append(d)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  {table}: {len(data)} rows -> {filename}")

tables = [row[0] for row in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()]

skip = {'players', 'player_islands', 'player_structures',
        'player_eggs', 'player_monsters', 'user_friends', 'users'}

print("Exporting game data tables:")
for t in tables:
    if t not in skip:
        export_table(t)

conn.close()
print(f"\nDone! Data exported to {OUTPUT_DIR}/")
