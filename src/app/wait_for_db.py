import sys
import time

from starlette_core.database import Database

from app.db import db


def connect():
    sys.stdout.write("Attempting database connection...\n")

    retries: int = 30
    sleep_interval: int = 2
    conn = None

    for i in range(1, retries + 1):
        sys.stdout.write(f"Attempt {i}...\n")
        try:
            conn = db.engine.connect()
            break
        except:
            i += 1
            time.sleep(sleep_interval)

    if conn:
        sys.stdout.write("Connected...\n")
        conn.close()
    else:
        sys.stderr.write("Failed to connect...\n")


if __name__ == "__main__":
    connect()
