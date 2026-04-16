import aiosqlite
from config import DATABASE_URL

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '📚',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                section_id INTEGER NOT NULL,
                correct_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                score REAL DEFAULT 0,
                finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id),
                FOREIGN KEY (section_id) REFERENCES sections(id)
            )
        """)
        await db.commit()

# ===================== USERS =====================

async def add_user(telegram_id: int, full_name: str, username: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, full_name, username)
            VALUES (?, ?, ?)
        """, (telegram_id, full_name, username))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
        return await cursor.fetchall()

async def get_users_count():
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]

# ===================== CATEGORIES =====================

async def get_all_categories():
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM categories WHERE is_active=1 ORDER BY id")
        return await cursor.fetchall()

async def get_category_by_id(cat_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM categories WHERE id=?", (cat_id,))
        return await cursor.fetchone()

async def add_category(name: str, emoji: str = "📚"):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()

async def delete_category(cat_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        await db.commit()

async def get_all_categories_admin():
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM categories ORDER BY id")
        return await cursor.fetchall()

# ===================== SECTIONS =====================

async def get_sections_by_category(cat_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            "SELECT * FROM sections WHERE category_id=? AND is_active=1 ORDER BY id", (cat_id,))
        return await cursor.fetchall()

async def get_section_by_id(sec_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM sections WHERE id=?", (sec_id,))
        return await cursor.fetchone()

async def add_section(category_id: int, name: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("INSERT INTO sections (category_id, name) VALUES (?, ?)", (category_id, name))
        await db.commit()

async def delete_section(sec_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("DELETE FROM sections WHERE id=?", (sec_id,))
        await db.commit()

async def get_sections_by_category_admin(cat_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            "SELECT * FROM sections WHERE category_id=? ORDER BY id", (cat_id,))
        return await cursor.fetchall()

# ===================== QUESTIONS =====================

async def get_questions_by_section(sec_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            "SELECT * FROM questions WHERE section_id=? ORDER BY id", (sec_id,))
        return await cursor.fetchall()

async def get_questions_count(sec_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM questions WHERE section_id=?", (sec_id,))
        row = await cursor.fetchone()
        return row[0]

async def add_question(section_id: int, question_text: str,
                       option_a: str, option_b: str, option_c: str, option_d: str,
                       correct_answer: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            INSERT INTO questions (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (section_id, question_text, option_a, option_b, option_c, option_d, correct_answer))
        await db.commit()

async def delete_question(q_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("DELETE FROM questions WHERE id=?", (q_id,))
        await db.commit()

async def get_question_by_id(q_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM questions WHERE id=?", (q_id,))
        return await cursor.fetchone()

# ===================== TEST RESULTS =====================

async def save_test_result(user_id: int, section_id: int, correct: int, total: int):
    score = round((correct / total) * 100, 1) if total > 0 else 0
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            INSERT INTO test_results (user_id, section_id, correct_count, total_count, score)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, section_id, correct, total, score))
        await db.commit()

async def get_user_results(user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            SELECT tr.*, s.name as section_name, c.name as category_name
            FROM test_results tr
            JOIN sections s ON tr.section_id = s.id
            JOIN categories c ON s.category_id = c.id
            WHERE tr.user_id = ?
            ORDER BY tr.finished_at DESC
            LIMIT 10
        """, (user_id,))
        return await cursor.fetchall()

async def get_top_results(section_id: int, limit: int = 10):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            SELECT tr.score, tr.correct_count, tr.total_count, u.full_name, tr.finished_at
            FROM test_results tr
            JOIN users u ON tr.user_id = u.telegram_id
            WHERE tr.section_id = ?
            ORDER BY tr.score DESC, tr.finished_at ASC
            LIMIT ?
        """, (section_id, limit))
        return await cursor.fetchall()

async def get_total_tests_count():
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM test_results")
        row = await cursor.fetchone()
        return row[0]
