import sqlite3
import os

# Location of the SQLite database file.
# Defaults to a "jobs.db" next to the code (original behaviour), but can be
# overridden via the JOBS_DB_PATH environment variable. This lets containerized
# deployments point the DB at a mounted volume so state survives restarts.
DB_FILE = os.getenv(
    "JOBS_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs.db"),
)

# Ensure the parent directory exists (e.g. when pointing at a mounted volume path).
_db_dir = os.path.dirname(os.path.abspath(DB_FILE))
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)

def get_connection():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    """Initializes the database tables."""
    connection = get_connection()
    cursor = connection.cursor()
    
    # Table for processed jobs (deduplication)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            post_date TEXT,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for active channel search queries (auto-update targets)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_searches (
            channel_id INTEGER PRIMARY KEY,
            keywords TEXT,
            location TEXT,
            last_checked TIMESTAMP
        )
    ''')
    
    # Table for user job selections/actions (Selectat / Aplicat buttons)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_selections (
            job_id TEXT,
            user_id INTEGER,
            user_name TEXT,
            status TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (job_id, user_id)
        )
    ''')
    
    connection.commit()
    connection.close()

# --- Jobs Deduplication ---

def is_job_added(job_id):
    if not job_id:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_job(job_id, title, company, location, post_date, link):
    if not job_id:
        return
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (job_id, title, company, location, post_date, link)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (job_id, title, company, location, post_date, link))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding job to database: {e}")
    finally:
        conn.close()

# --- Active Searches ---

def save_active_search(channel_id, keywords, location):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO active_searches (channel_id, keywords, location)
        VALUES (?, ?, ?)
    ''', (channel_id, keywords, location))
    conn.commit()
    conn.close()

def get_active_searches():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, keywords, location FROM active_searches")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Job Button Selections ---

def toggle_job_selection(job_id, user_id, user_name, new_status):
    """Toggles or updates status ('Selectat' or 'Aplicat') for a job by user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT status FROM job_selections WHERE job_id = ? AND user_id = ?", (job_id, user_id))
    row = cursor.fetchone()
    
    if row and row['status'] == new_status:
        # If user clicks the same button again, unselect/remove status
        cursor.execute("DELETE FROM job_selections WHERE job_id = ? AND user_id = ?", (job_id, user_id))
        final_status = None
    else:
        # Set or update to new status
        cursor.execute('''
            INSERT OR REPLACE INTO job_selections (job_id, user_id, user_name, status)
            VALUES (?, ?, ?, ?)
        ''', (job_id, user_id, user_name, new_status))
        final_status = new_status
        
    conn.commit()
    conn.close()
    return final_status

def get_job_statuses(job_id):
    """Returns a list of dicts with user selections for a given job."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_name, status FROM job_selections WHERE job_id = ?", (job_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
