"""Apply migrations only to the dedicated, freshly initialized local test cluster."""
from pathlib import Path
import psycopg

def main():
    with psycopg.connect("host=127.0.0.1 port=55432 user=portfolio_test dbname=postgres",autocommit=True) as db:
        with db.cursor() as cursor:
            cursor.execute("select exists(select 1 from pg_roles where rolname='anon')")
            if cursor.fetchone()[0]: raise SystemExit("Bootstrap already applied; use the existing isolated database")
            cursor.execute("create role anon nologin")
            cursor.execute("create role authenticated nologin")
            cursor.execute("create database portfolio_rls_test")
    with psycopg.connect("host=127.0.0.1 port=55432 user=portfolio_test dbname=portfolio_rls_test",autocommit=True) as db:
        with db.cursor() as cursor:
            for path in sorted(Path("supabase/migrations").glob("*.sql")):
                cursor.execute(path.read_text(encoding="utf-8"))
    print("Isolated test migrations applied")

if __name__=="__main__": main()
