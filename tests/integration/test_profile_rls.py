import pytest
import psycopg

pytestmark=pytest.mark.rls

@pytest.mark.parametrize("role",["anon","authenticated"])
def test_profile_permissions_and_withdrawal(isolated_db,role):
    db=isolated_db
    with db.cursor() as cursor:
        cursor.execute("update private.profile_test_drafts set summary='EDITED_PRIVATE_SENTINEL'")
        cursor.execute("set local role "+role)
        cursor.execute("select * from public.public_profiles where id='11111111-1111-4111-8111-111111111111'")
        rows=cursor.fetchall()
        assert len(rows)==1 and "PRIVATE" not in repr(rows)
        for sql in ("select * from private.profile_test_drafts","update public.public_profiles set full_name='ATTACK'","delete from public.public_profiles","insert into public.public_profiles(full_name,degree) values ('ATTACK','ATTACK')"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with db.transaction(): cursor.execute(sql)
        cursor.execute("reset role")
        cursor.execute("select full_name,summary from public.public_profiles")
        assert cursor.fetchone()==("Persona sintética","Instantánea aprobada")
        cursor.execute("update public.public_profiles set published_at=null")
        cursor.execute("set local role "+role)
        cursor.execute("select * from public.public_profiles")
        assert cursor.fetchall()==[]
