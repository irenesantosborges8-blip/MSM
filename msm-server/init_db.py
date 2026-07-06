#!/usr/bin/env python3
import sqlite3
import os
import json
import shutil

DB_PATH = "server-data/msm_server.db"
GAME_DB_SOURCE = "/workspaces/MSM/open-source-servers/database/static/zewmsm_4.8.0_20250430.db"

def get_conn(path):
    return sqlite3.connect(path)

def init_game_tables(conn):
    cur = conn.cursor()
    tables = [
        """
        CREATE TABLE IF NOT EXISTS monsters (
            entity_id INTEGER, entity_type TEXT, name TEXT, common_name TEXT,
            class_name TEXT, genes TEXT, description TEXT,
            cost_diamonds INTEGER, cost_coins INTEGER, cost_keys INTEGER,
            cost_sale INTEGER, cost_starpower INTEGER, cost_medals INTEGER,
            cost_relics INTEGER, cost_eth_currency INTEGER,
            view_in_market INTEGER, view_in_starmarket INTEGER,
            premium INTEGER, box_monster INTEGER, movable INTEGER,
            requirements TEXT, happiness TEXT, min_level INTEGER,
            levelup_island TEXT, graphic TEXT, portrait_graphic TEXT,
            spore_graphic TEXT, select_sound TEXT, size_x INTEGER, size_y INTEGER,
            y_offset INTEGER, build_time INTEGER, beds INTEGER, xp INTEGER,
            time_to_fill_sec INTEGER, keywords TEXT, min_server_version TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS structures (
            name TEXT, description TEXT, entity_id INTEGER, entity_type TEXT,
            level INTEGER, structure_type TEXT, graphic TEXT, sound TEXT,
            y_offset INTEGER, cost_coins INTEGER, cost_diamonds INTEGER,
            cost_eth_currency INTEGER, cost_keys INTEGER, cost_medals INTEGER,
            cost_relics INTEGER, cost_sale INTEGER, cost_starpower INTEGER,
            premium INTEGER, build_time INTEGER, battle_level INTEGER,
            upgrades_to INTEGER, allowed_on_island TEXT, requirements TEXT,
            min_server_version TEXT, movable INTEGER, sellable INTEGER,
            show_in_levelup INTEGER, view_in_market INTEGER,
            view_in_starmarket INTEGER, platforms TEXT, size_x INTEGER,
            size_y INTEGER, extra TEXT, last_changed INTEGER, xp INTEGER,
            id INTEGER PRIMARY KEY, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS islands (
            name TEXT, short_name TEXT, description TEXT,
            first_time_visit_desc TEXT, first_time_visit_menu TEXT,
            cost_coins INTEGER, cost_keys INTEGER, cost_relics INTEGER,
            cost_diamonds INTEGER, cost_starpower INTEGER, cost_medals INTEGER,
            cost_eth_currency INTEGER, min_level INTEGER, min_server_version TEXT,
            enabled INTEGER, island_type INTEGER, island_lock INTEGER,
            has_nursery_scratch INTEGER, has_book INTEGER, graphic TEXT,
            iconSheet TEXT, iconSprite TEXT, torch_graphic TEXT, midi TEXT,
            ambient_track TEXT, castle_structure_id INTEGER, grid TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS genes (
            gene_graphic TEXT, gene_string TEXT, gene_letter TEXT,
            sort_order INTEGER, min_server_version TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS levels (
            xp INTEGER, title TEXT, max_bakeries INTEGER,
            last_changed INTEGER, id INTEGER PRIMARY KEY, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS rare_monster_data (
            rare_id INTEGER, id INTEGER PRIMARY KEY,
            last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS epic_monster_data (
            epic_id INTEGER, id INTEGER PRIMARY KEY,
            last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS entity_alt_costs (
            cost_coins INTEGER, cost_keys INTEGER, cost_eth_currency INTEGER,
            cost_diamonds INTEGER, cost_relics INTEGER, cost_starpower INTEGER,
            entity_id INTEGER, island INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS island_theme_data (
            name TEXT, theme_id INTEGER, island INTEGER, storeitem_id INTEGER,
            cost_coins INTEGER, cost_keys INTEGER, cost_diamonds INTEGER,
            cost_starpower INTEGER, cost_eth_currency INTEGER, cost_relics INTEGER,
            level INTEGER, view_in_market INTEGER, unlocked_entities TEXT,
            description TEXT, modifier_description TEXT, modifiers TEXT,
            trees TEXT, rocks TEXT, placement_id TEXT, graphic TEXT,
            season_event_name TEXT, month_string TEXT, version TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS store_items (
            amount INTEGER, unlock_level INTEGER, item_desc TEXT, max INTEGER,
            ios_platform_id TEXT, item_name TEXT, enabled INTEGER,
            most_popular_priority INTEGER, contents TEXT, group_id INTEGER,
            sheet_id TEXT, android_platform_id TEXT, price INTEGER,
            consumable INTEGER, best_value_priority INTEGER, currency TEXT,
            exclude INTEGER, item_title TEXT, image_id TEXT,
            min_server_version TEXT, currency_id INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS store_groups (
            group_title TEXT, group_name TEXT, ad_name TEXT, currency INTEGER,
            min_server_version TEXT, store_ordering INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS store_currencies (
            currency_name TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS store_replacements (
            numOwnedBeforeReplacement INTEGER, entityIdSource TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS game_settings (
            id INTEGER PRIMARY KEY, key TEXT UNIQUE, value TEXT,
            last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS monster_levels (
            id INTEGER PRIMARY KEY, monster_id INTEGER, level INTEGER,
            coins INTEGER, max_coins INTEGER, food INTEGER,
            max_ethereal INTEGER, ethereal_currency INTEGER,
            last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS monster_home_data (
            id INTEGER PRIMARY KEY, source_monster INTEGER, dest_monster INTEGER,
            source_island INTEGER, dest_island INTEGER,
            last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS island_monsters (
            id INTEGER PRIMARY KEY, island_id INTEGER, monster INTEGER,
            bom INTEGER, book_y INTEGER, book_x INTEGER, instrument TEXT,
            book_flip INTEGER, book_z INTEGER,
            last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS island_structures (
            id INTEGER PRIMARY KEY, island_id INTEGER, structure INTEGER,
            instrument TEXT, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS costumes (
            min_version TEXT, ignore_locks INTEGER, always_visible INTEGER,
            hidden INTEGER, keywords TEXT, medalCost INTEGER, sellCost INTEGER,
            etherealSellCost INTEGER, diamondCost INTEGER, alt_icon_name TEXT,
            unlock_teleport INTEGER, breed_chance REAL, file TEXT,
            monster_id INTEGER, alt_text TEXT, name TEXT, action INTEGER,
            alt_icon_sheet TEXT, common_name TEXT, unlock_purchased INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS flex_eggs (
            cost_coins INTEGER, cost_diamonds INTEGER, xp INTEGER,
            mastertext_desc TEXT, _def TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS attuner_genes (
            schedule TEXT, critter_graphic TEXT, gene TEXT,
            attuner_graphic TEXT, instability INTEGER, island_id INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS scratch_offers (
            amount INTEGER, sheetName TEXT, probability INTEGER,
            is_top_prize INTEGER, spriteName TEXT, revealSfx TEXT,
            type TEXT, prize TEXT, min_server_version TEXT,
            last_changed INTEGER, id INTEGER PRIMARY KEY, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS flip_boards (
            name TEXT, definition TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS flip_levels (
            num_dipsters INTEGER, num_sigils INTEGER, shape TEXT,
            level INTEGER, columns INTEGER, rows INTEGER, num_epics INTEGER,
            mismatches_allowed INTEGER, num_rares INTEGER, prize_pool INTEGER,
            last_changed INTEGER, id INTEGER PRIMARY KEY, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_cumulative_logins (
            name TEXT, layout TEXT, rewards TEXT, min_version TEXT,
            island INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS nucleus_rewards (
            types TEXT,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tital_soul_levels (
            min_links INTEGER, power INTEGER, song_part INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS timed_events (
            start_date INTEGER, end_date INTEGER, event_type TEXT,
            data TEXT, event_id INTEGER,
            id INTEGER PRIMARY KEY, last_changed INTEGER, date_created INTEGER
        )
        """,
    ]
    for t in tables:
        cur.execute(t)
    conn.commit()

def init_user_tables(conn):
    cur = conn.cursor()
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            bbb_id INTEGER PRIMARY KEY,
            user_game_id TEXT UNIQUE,
            username TEXT,
            password TEXT,
            login_type TEXT DEFAULT 'anon',
            date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            active_island INTEGER DEFAULT -1,
            display_name TEXT DEFAULT 'New Player',
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 100000,
            diamonds INTEGER DEFAULT 1000,
            food INTEGER DEFAULT 100000,
            keys INTEGER DEFAULT 100,
            relics INTEGER DEFAULT 100,
            starpower INTEGER DEFAULT 0,
            ethereal_currency INTEGER DEFAULT 0,
            egg_wildcards INTEGER DEFAULT 0,
            battle_level INTEGER DEFAULT 1,
            battle_xp INTEGER DEFAULT 0,
            battle_medals INTEGER DEFAULT 0,
            premium INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            country TEXT DEFAULT 'BR',
            client_platform TEXT DEFAULT 'pc',
            nickname TEXT DEFAULT 'New Player',
            last_login INTEGER DEFAULT 0,
            date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS player_islands (
            user_island_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_game_id TEXT,
            island_id INTEGER DEFAULT 1,
            name TEXT,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0,
            warp_speed REAL DEFAULT 1.0,
            monsters_sold TEXT DEFAULT '[]',
            date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS player_monsters (
            user_monster_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_game_id TEXT,
            user_island_id INTEGER,
            monster_id INTEGER,
            level INTEGER DEFAULT 1,
            pos_x INTEGER DEFAULT 0,
            pos_y INTEGER DEFAULT 0,
            flip INTEGER DEFAULT 0,
            muted INTEGER DEFAULT 0,
            name TEXT DEFAULT 'Monster',
            volume REAL DEFAULT 1.0,
            last_collection INTEGER DEFAULT 0,
            date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS player_structures (
            user_structure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_game_id TEXT,
            user_island_id INTEGER,
            structure_id INTEGER,
            pos_x INTEGER DEFAULT 0,
            pos_y INTEGER DEFAULT 0,
            flip INTEGER DEFAULT 0,
            scale REAL DEFAULT 1.0,
            muted INTEGER DEFAULT 0,
            is_complete INTEGER DEFAULT 1,
            is_upgrading INTEGER DEFAULT 0,
            name TEXT DEFAULT 'Structure',
            date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS player_eggs (
            user_egg_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_game_id TEXT,
            user_island_id INTEGER,
            user_structure_id INTEGER DEFAULT 0,
            monster_id INTEGER,
            date_created INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_1 INTEGER,
            user_2 INTEGER,
            date_created INTEGER
        )
        """,
    ]
    for t in tables:
        cur.execute(t)
    conn.commit()

def import_game_data(target_conn):
    if not os.path.exists(GAME_DB_SOURCE):
        print(f"Source DB not found: {GAME_DB_SOURCE}, skipping import")
        return
    source_conn = get_conn(GAME_DB_SOURCE)
    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()

    tables = [row[0] for row in source_cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]

    skip_tables = {'players', 'player_islands', 'player_structures',
                   'player_eggs', 'player_monsters', 'sqlite_sequence'}

    for table in tables:
        if table in skip_tables:
            continue
        rows = source_cur.execute(f"SELECT * FROM [{table}]").fetchall()
        if not rows:
            continue
        col_names = [desc[0] for desc in source_cur.description]
        placeholders = ','.join(['?' for _ in col_names])
        cols = ','.join([f'"{c}"' for c in col_names])
        target_cur.execute(f"DELETE FROM [{table}]")
        for row in rows:
            clean = tuple(None if isinstance(v, bytes) else v for v in row)
            target_cur.execute(
                f"INSERT OR IGNORE INTO [{table}] ({cols}) VALUES ({placeholders})",
                clean
            )
    target_conn.commit()
    source_conn.close()
    print(f"Imported {len(tables)} game tables")

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn(DB_PATH)
    init_game_tables(conn)
    init_user_tables(conn)
    import_game_data(conn)
    conn.close()
    print(f"Database created: {DB_PATH}")
    size = os.path.getsize(DB_PATH)
    print(f"Size: {size:,} bytes")

if __name__ == "__main__":
    main()
