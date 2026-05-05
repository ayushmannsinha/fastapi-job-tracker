from pathlib import Path
import sys

from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import engine


INTEGER_PRIMARY_KEYS = (
    ("users", "id"),
    ("jobs", "id"),
    ("resumes", "id"),
    ("applications", "id"),
    ("matchscores", "id"),
)


def repair_integer_primary_key(table_name: str, column_name: str) -> None:
    sequence_name = f"{table_name}_{column_name}_seq"

    with engine.begin() as conn:
        conn.execute(
            text(
                f"""
                CREATE SEQUENCE IF NOT EXISTS {sequence_name};

                SELECT setval(
                    '{sequence_name}',
                    COALESCE((SELECT MAX({column_name}) FROM {table_name}), 0) + 1,
                    false
                );

                ALTER TABLE {table_name}
                    ALTER COLUMN {column_name}
                    SET DEFAULT nextval('{sequence_name}');

                ALTER SEQUENCE {sequence_name}
                    OWNED BY {table_name}.{column_name};
                """
            )
        )


def main() -> None:
    for table_name, column_name in INTEGER_PRIMARY_KEYS:
        repair_integer_primary_key(table_name, column_name)

    print("PostgreSQL primary-key defaults repaired.")


if __name__ == "__main__":
    main()
