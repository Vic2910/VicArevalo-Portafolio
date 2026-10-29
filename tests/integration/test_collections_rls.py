import pytest
import psycopg

pytestmark=pytest.mark.rls

@pytest.mark.parametrize("role",["anon","authenticated"])
def test_collection_policies(isolated_db,role):
    db=isolated_db
    with db.cursor() as cursor:
        cursor.execute("set local role "+role)
        for table,field in (("public_skills","name"),("public_academic_experiences","activity")):
            cursor.execute(f"select * from public.{table}")
            assert len(cursor.fetchall())==1
            cursor.execute(f"select c.id from public.{table} c join public.public_profiles p on p.id=c.profile_id")
            assert len(cursor.fetchall())==1
            for sql in (f"update public.{table} set {field}='ATTACK'",f"delete from public.{table}",f"insert into public.{table}(profile_id,{field}) values ('11111111-1111-4111-8111-111111111111','ATTACK')"):
                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    with db.transaction(): cursor.execute(sql)
        cursor.execute("reset role")
        for table in ("public_skills","public_academic_experiences"):
            cursor.execute(f"select count(*) from public.{table}")
            assert cursor.fetchone()[0]==2
        cursor.execute("update public.public_profiles set published_at=null")
        cursor.execute("set local role "+role)
        for table in ("public_skills","public_academic_experiences"):
            cursor.execute(f"select * from public.{table} where profile_id='11111111-1111-4111-8111-111111111111'")
            assert cursor.fetchall()==[]
