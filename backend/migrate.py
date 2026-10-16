from pathlib import Path

from app.settings import get_db_conn

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def main() -> None:
    with get_db_conn() as conn:
        conn.autocommit = True
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY)"
        )
        rows = conn.execute("SELECT filename FROM schema_migrations").fetchall()
        already_applied = {row[0] for row in rows}

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in already_applied:
                continue
            with conn.transaction():
                conn.execute(path.read_text(encoding="utf-8"))
                conn.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s)",
                    (path.name,),
                )
            print(f"applied {path.name}")


if __name__ == "__main__":
    main()
