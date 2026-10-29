import os
from pathlib import Path
import pytest
import psycopg

@pytest.fixture
def isolated_db():
    if os.getenv("TEST_ISOLATED")!="1" or not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("RLS incompleta: requiere TEST_ISOLATED=1 y TEST_DATABASE_URL aislada")
    # Never print connection exceptions: DSNs may contain passwords.
    try: connection=psycopg.connect(os.environ["TEST_DATABASE_URL"])
    except Exception: pytest.fail("No se pudo conectar al entorno RLS aislado",pytrace=False)
    try:
        with connection.cursor() as cursor:
            cursor.execute("select count(*) from public.public_profiles")
            if cursor.fetchone()[0]: pytest.fail("RLS exige una base de prueba vacía",pytrace=False)
            for name in ("profile.sql","collections.sql"):
                cursor.execute((Path(__file__).parent/"fixtures"/name).read_text(encoding="utf-8"))
        yield connection
    finally:
        connection.rollback()
        connection.close()
