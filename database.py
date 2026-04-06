import sqlite3
import random

DATABASE_NAME = "fraud.db"

# ------------------ CONNECTION ------------------
def connect_db():
    return sqlite3.connect(DATABASE_NAME)


# ------------------ INITIALIZE TABLES ------------------
def initialize_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        mobile_number TEXT UNIQUE,
        password TEXT,
        mpin TEXT,
        account_number TEXT,
        balance REAL,
        wallet_balance REAL,
        avg_amount REAL,
        account_age INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT,
        receiver_id TEXT,
        amount REAL,
        risk_score INTEGER,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# ------------------ REGISTER USER ------------------
def register_user(name, mobile, password, mpin):
    conn = connect_db()
    cursor = conn.cursor()

    # Check if mobile already exists
    cursor.execute("SELECT user_id FROM users WHERE mobile_number = ?", (mobile,))
    if cursor.fetchone():
        conn.close()
        raise Exception("Mobile number already registered")

    user_id = "U" + str(random.randint(10000, 99999))
    account_number = str(random.randint(1000000000, 9999999999))

    cursor.execute("""
    INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, name, mobile, password, mpin,
        account_number,
        5000,   # default bank balance
        1000,   # default wallet balance
        1000,   # avg amount
        10      # account age (new user = risky)
    ))

    conn.commit()
    conn.close()
    return user_id


# ------------------ LOGIN USER ------------------
def login_user(mobile, mpin):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id, name, balance, wallet_balance, account_number
    FROM users WHERE mobile_number = ? AND mpin = ?
    """, (mobile, mpin))

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "user_id": user[0],
            "name": user[1],
            "balance": user[2],
            "wallet_balance": user[3],
            "account_number": user[4]
        }
    return None


# ------------------ FETCH SINGLE USER ------------------
def fetch_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "user_id": user[0],
            "name": user[1],
            "mobile": user[2],
            "account_number": user[5],
            "balance": user[6],
            "wallet_balance": user[7],
            "avg_amount": user[8],
            "account_age": user[9]
        }
    return None


# ------------------ FETCH USERS LIST ------------------
def fetch_users(limit=100):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name FROM users LIMIT ?", (limit,))
    users = cursor.fetchall()
    conn.close()
    return users


# ------------------ SAVE TRANSACTION ------------------
def insert_transaction(sender_id, receiver_id, amount, risk_score, status):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions (sender_id, receiver_id, amount, risk_score, status)
    VALUES (?, ?, ?, ?, ?)
    """, (sender_id, receiver_id, amount, risk_score, status))

    # Deduct balance from sender if SUCCESS or WARNING
    if status in ("SUCCESS", "WARNING"):
        cursor.execute("""
        UPDATE users SET balance = balance - ? WHERE user_id = ?
        """, (amount, sender_id))

        cursor.execute("""
        UPDATE users SET balance = balance + ? WHERE user_id = ?
        """, (amount, receiver_id))

    conn.commit()
    conn.close()


# ------------------ FETCH TRANSACTIONS ------------------
def fetch_transactions(limit=20):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sender_id, receiver_id, amount, risk_score, status, timestamp
    FROM transactions
    ORDER BY txn_id DESC LIMIT ?
    """, (limit,))

    transactions = cursor.fetchall()
    conn.close()
    return transactions


# ------------------ RUN ONCE TO INIT ------------------
if __name__ == "__main__":
    initialize_database()
    print("Database ready.")