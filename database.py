import sqlite3

def get_connection():
    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            post_date DATETIME,
            link TEXT
        )
    ''')
    connection.commit()
    connection.close()

def is_job_added(job_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
    result = cursor.fetchone()
    connection.close()
    return result is not None

def add_job(job_id, title, company, location, post_date, link):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO jobs (job_id, title, company, location, post_date, link)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (job_id, title, company, location, post_date, link))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error adding job to database: {e}")
    finally:
        connection.close()  

