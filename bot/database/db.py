import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict
import config


class Database:
    def __init__(self):
        self.path = config.DATABASE_PATH
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self._create_tables()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def _create_tables(self):
        async with self.conn.cursor() as cur:
            await cur.execute("""CREATE TABLE IF NOT EXISTS afk (user_id INTEGER PRIMARY KEY, is_afk INTEGER DEFAULT 0, reason TEXT, since TEXT)""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, name TEXT, content TEXT, UNIQUE(chat_id, name))""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS filters (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, keyword TEXT, reply TEXT, UNIQUE(chat_id, keyword))""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS welcomes (chat_id INTEGER PRIMARY KEY, enabled INTEGER DEFAULT 1, message TEXT, clean_service INTEGER DEFAULT 0)""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS autodelete (chat_id INTEGER PRIMARY KEY, enabled INTEGER DEFAULT 0, delay INTEGER DEFAULT 3600)""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS schedules (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER, message TEXT, run_at TEXT, is_done INTEGER DEFAULT 0, created_at TEXT)""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS antispam (user_id INTEGER, chat_id INTEGER, warnings INTEGER DEFAULT 0, last_message TEXT, PRIMARY KEY (user_id, chat_id))""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS gban (user_id INTEGER PRIMARY KEY, reason TEXT, banned_by INTEGER, banned_at TEXT)""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS user_settings (user_id INTEGER PRIMARY KEY, language TEXT DEFAULT 'en', timezone TEXT DEFAULT 'Asia/Kolkata')""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS approved (user_id INTEGER PRIMARY KEY, approved_by INTEGER, approved_at TEXT)""")
            await cur.execute("""CREATE TABLE IF NOT EXISTS chat_flags (chat_id INTEGER, flag TEXT, value INTEGER DEFAULT 0, PRIMARY KEY (chat_id, flag))""")
            await self.conn.commit()

    async def set_afk(self, user_id: int, reason: str = None):
        since = datetime.utcnow().isoformat()
        await self.conn.execute("INSERT OR REPLACE INTO afk (user_id, is_afk, reason, since) VALUES (?, 1, ?, ?)", (user_id, reason or config.AFK_DEFAULT_REASON, since))
        await self.conn.commit()

    async def unset_afk(self, user_id: int):
        await self.conn.execute("UPDATE afk SET is_afk = 0 WHERE user_id = ?", (user_id,))
        await self.conn.commit()

    async def get_afk(self, user_id: int) -> Optional[Dict]:
        async with self.conn.execute("SELECT * FROM afk WHERE user_id = ? AND is_afk = 1", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def save_note(self, chat_id: int, name: str, content: str):
        await self.conn.execute("INSERT OR REPLACE INTO notes (chat_id, name, content) VALUES (?, ?, ?)", (chat_id, name.lower(), content))
        await self.conn.commit()

    async def get_note(self, chat_id: int, name: str) -> Optional[str]:
        async with self.conn.execute("SELECT content FROM notes WHERE chat_id = ? AND name = ?", (chat_id, name.lower())) as cur:
            row = await cur.fetchone()
            return row["content"] if row else None

    async def delete_note(self, chat_id: int, name: str) -> bool:
        cur = await self.conn.execute("DELETE FROM notes WHERE chat_id = ? AND name = ?", (chat_id, name.lower()))
        await self.conn.commit()
        return cur.rowcount > 0

    async def list_notes(self, chat_id: int) -> List[str]:
        async with self.conn.execute("SELECT name FROM notes WHERE chat_id = ? ORDER BY name", (chat_id,)) as cur:
            rows = await cur.fetchall()
            return [r["name"] for r in rows]

    async def save_filter(self, chat_id: int, keyword: str, reply: str):
        await self.conn.execute("INSERT OR REPLACE INTO filters (chat_id, keyword, reply) VALUES (?, ?, ?)", (chat_id, keyword.lower(), reply))
        await self.conn.commit()

    async def get_filter(self, chat_id: int, keyword: str) -> Optional[str]:
        async with self.conn.execute("SELECT reply FROM filters WHERE chat_id = ? AND keyword = ?", (chat_id, keyword.lower())) as cur:
            row = await cur.fetchone()
            return row["reply"] if row else None

    async def get_all_filters(self, chat_id: int) -> List[Dict]:
        async with self.conn.execute("SELECT keyword, reply FROM filters WHERE chat_id = ?", (chat_id,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def delete_filter(self, chat_id: int, keyword: str) -> bool:
        cur = await self.conn.execute("DELETE FROM filters WHERE chat_id = ? AND keyword = ?", (chat_id, keyword.lower()))
        await self.conn.commit()
        return cur.rowcount > 0

    async def set_welcome(self, chat_id: int, message: str, enabled: bool = True):
        await self.conn.execute("INSERT OR REPLACE INTO welcomes (chat_id, enabled, message) VALUES (?, ?, ?)", (chat_id, 1 if enabled else 0, message))
        await self.conn.commit()

    async def get_welcome(self, chat_id: int) -> Optional[Dict]:
        async with self.conn.execute("SELECT * FROM welcomes WHERE chat_id = ?", (chat_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def toggle_welcome(self, chat_id: int, enabled: bool):
        await self.conn.execute("UPDATE welcomes SET enabled = ? WHERE chat_id = ?", (1 if enabled else 0, chat_id))
        await self.conn.commit()

    async def set_autodelete(self, chat_id: int, enabled: bool, delay: int = 3600):
        await self.conn.execute("INSERT OR REPLACE INTO autodelete (chat_id, enabled, delay) VALUES (?, ?, ?)", (chat_id, 1 if enabled else 0, delay))
        await self.conn.commit()

    async def get_autodelete(self, chat_id: int) -> Optional[Dict]:
        async with self.conn.execute("SELECT * FROM autodelete WHERE chat_id = ?", (chat_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def add_schedule(self, chat_id: int, user_id: int, message: str, run_at: str) -> int:
        created = datetime.utcnow().isoformat()
        cur = await self.conn.execute("INSERT INTO schedules (chat_id, user_id, message, run_at, created_at) VALUES (?, ?, ?, ?, ?)", (chat_id, user_id, message, run_at, created))
        await self.conn.commit()
        return cur.lastrowid

    async def get_pending_schedules(self) -> List[Dict]:
        now = datetime.utcnow().isoformat()
        async with self.conn.execute("SELECT * FROM schedules WHERE is_done = 0 AND run_at <= ? ORDER BY run_at", (now,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def mark_schedule_done(self, schedule_id: int):
        await self.conn.execute("UPDATE schedules SET is_done = 1 WHERE id = ?", (schedule_id,))
        await self.conn.commit()

    async def list_schedules(self, user_id: int) -> List[Dict]:
        async with self.conn.execute("SELECT * FROM schedules WHERE user_id = ? AND is_done = 0 ORDER BY run_at", (user_id,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def delete_schedule(self, schedule_id: int, user_id: int) -> bool:
        cur = await self.conn.execute("DELETE FROM schedules WHERE id = ? AND user_id = ?", (schedule_id, user_id))
        await self.conn.commit()
        return cur.rowcount > 0

    async def get_warnings(self, user_id: int, chat_id: int) -> int:
        async with self.conn.execute("SELECT warnings FROM antispam WHERE user_id = ? AND chat_id = ?", (user_id, chat_id)) as cur:
            row = await cur.fetchone()
            return row["warnings"] if row else 0

    async def add_warning(self, user_id: int, chat_id: int) -> int:
        current = await self.get_warnings(user_id, chat_id)
        new_count = current + 1
        await self.conn.execute("""INSERT INTO antispam (user_id, chat_id, warnings, last_message) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, chat_id) DO UPDATE SET warnings = ?""", (user_id, chat_id, new_count, datetime.utcnow().isoformat(), new_count))
        await self.conn.commit()
        return new_count

    async def reset_warnings(self, user_id: int, chat_id: int):
        await self.conn.execute("DELETE FROM antispam WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
        await self.conn.commit()

    async def gban_user(self, user_id: int, reason: str, banned_by: int):
        await self.conn.execute("INSERT OR REPLACE INTO gban (user_id, reason, banned_by, banned_at) VALUES (?, ?, ?, ?)", (user_id, reason, banned_by, datetime.utcnow().isoformat()))
        await self.conn.commit()

    async def ungban_user(self, user_id: int) -> bool:
        cur = await self.conn.execute("DELETE FROM gban WHERE user_id = ?", (user_id,))
        await self.conn.commit()
        return cur.rowcount > 0

    async def is_gbanned(self, user_id: int) -> Optional[Dict]:
        async with self.conn.execute("SELECT * FROM gban WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def approve_user(self, user_id: int, approved_by: int):
        await self.conn.execute("INSERT OR REPLACE INTO approved (user_id, approved_by, approved_at) VALUES (?, ?, ?)", (user_id, approved_by, datetime.utcnow().isoformat()))
        await self.conn.commit()

    async def disapprove_user(self, user_id: int) -> bool:
        cur = await self.conn.execute("DELETE FROM approved WHERE user_id = ?", (user_id,))
        await self.conn.commit()
        return cur.rowcount > 0

    async def is_approved(self, user_id: int) -> bool:
        async with self.conn.execute("SELECT 1 FROM approved WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone() is not None

    async def set_chat_flag(self, chat_id: int, flag: str, value: bool):
        await self.conn.execute("""INSERT INTO chat_flags (chat_id, flag, value) VALUES (?, ?, ?) ON CONFLICT(chat_id, flag) DO UPDATE SET value = ?""", (chat_id, flag, 1 if value else 0, 1 if value else 0))
        await self.conn.commit()

    async def get_chat_flag(self, chat_id: int, flag: str, default: bool = False) -> bool:
        async with self.conn.execute("SELECT value FROM chat_flags WHERE chat_id = ? AND flag = ?", (chat_id, flag)) as cur:
            row = await cur.fetchone()
            if row is None: return default
            return bool(row["value"])
