import sqlite3
from pathlib import Path
import argparse

BATCH_SIZE = 1000  # commit every N files for efficiency

def ingest_files(data_dir: Path, db_path: str):
    """
    Scan data_dir recursively for JSON files and insert entries
    (timestamp, system_id, filepath) into SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    files_to_insert = []

    for file in data_dir.rglob("*.json"):
        try:
            filename = Path(file).stem
            filename = filename.split("_")
            system_id = filename[0]
            timestamp = filename[1]


        except ValueError:
            print(f"Skipping {str(file.absolute())}, invalid timestamp in filename")
            continue

        files_to_insert.append((timestamp, system_id, str(file.absolute())))

        if len(files_to_insert) >= BATCH_SIZE:
            cursor.executemany(
                "INSERT INTO snapshots (time, system_id, filepath) VALUES (?, ?, ?)",
                files_to_insert
            )
            conn.commit()
            files_to_insert = []

    if files_to_insert:
        cursor.executemany(
            "INSERT INTO snapshots (time, system_id, filepath) VALUES (?, ?, ?)",
            files_to_insert
        )
        conn.commit()

    conn.close()
    print(f"Ingestion completed for data_dir='{data_dir}' into db='{db_path}'")

def main():
    parser = argparse.ArgumentParser(description="Ingest JSON snapshots into SQLite database")
    parser.add_argument("--data_dir", type=Path, required=True,
                        help="Root directory containing system folders with JSON files")
    parser.add_argument("--db_path", type=str, default="snapshots.db",
                        help="Path to SQLite database (will be created if missing)")
    args = parser.parse_args()

    # Create DB and table if not exists
    conn = sqlite3.connect(args.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            time TEXT NOT NULL,
            system_id TEXT NOT NULL,
            filepath TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_time ON snapshots(time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_time ON snapshots(system_id, time)")
    conn.commit()
    conn.close()

    # Run ingestion
    ingest_files(args.data_dir, args.db_path)

if __name__ == "__main__":
    main()