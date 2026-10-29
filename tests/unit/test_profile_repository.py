from types import SimpleNamespace
import pytest
import httpx
from app.public.repository import PublicRepository
from app.config import PublicConfig

ROW=dict(id="11111111-1111-4111-8111-111111111111",full_name="Persona sintética",degree="Carrera",summary=None,public_contacts=[],published_at="2026-10-27T00:00:00Z")

class Query:
    def __init__(self, responses):
        self.responses=iter(responses)
        self.calls=[]
    @property
    def not_(self):
        self.calls.append(("not_",(),{}))
        return self
    def __getattr__(self,name):
        def operation(*args,**kwargs):
            self.calls.append((name,args,kwargs))
            if name=="execute":
                value=next(self.responses)
                if isinstance(value,Exception): raise value
                return SimpleNamespace(data=value)
            return self
        return operation

def repository(responses,clock=lambda:0):
    query=Query(responses)
    repo=PublicRepository(PublicConfig("https://test.supabase.co","sb_publishable_test",6),clock=clock,client_factory=lambda remaining:query)
    return repo,query

@pytest.mark.parametrize("rows,state",[([],"empty"),([ROW],"ready"),([ROW,ROW],"unavailable"),([{}],"unavailable"),([dict(ROW,full_name="[PENDIENTE]")],"unavailable")])
def test_profile_shape(rows,state):
    repo,query=repository([rows])
    assert repo.get_profile().state==state
    assert any(name=="select" and "*" not in args[0] for name,args,_ in query.calls)
    assert any(name=="is_" and args==("published_at","null") for name,args,_ in query.calls)
    assert sum(name=="execute" for name,_,_ in query.calls)==1

@pytest.mark.parametrize("error",[httpx.ReadTimeout("PRIVATE_SENTINEL"),RuntimeError("429 PRIVATE_SENTINEL"),RuntimeError("HTTP PRIVATE_SENTINEL")])
def test_failure_sanitized(error,caplog):
    repo,query=repository([error])
    result=repo.get_profile()
    assert result.state=="unavailable"
    assert "PRIVATE_SENTINEL" not in repr(result)+caplog.text
    assert sum(name=="execute" for name,_,_ in query.calls)==1

def test_absent_configuration():
    assert PublicRepository(PublicConfig(None,None,6)).get_profile().state=="unavailable"

@pytest.mark.parametrize("contact",[{"kind":"https","label":"Sitio","value":"javascript:alert(1)"},{"kind":"email","label":"Correo","value":"a@b.com\r\nBcc:x@y.com"},{"kind":"phone","label":"Teléfono","value":"data:test"}])
def test_invalid_contact(contact):
    repo,_=repository([[dict(ROW,public_contacts=[contact])]])
    assert repo.get_profile().state=="unavailable"

def test_shared_deadline():
    values=iter([0,7])
    repo,query=repository([],clock=lambda:next(values))
    assert repo.get_profile().state=="unavailable"
    assert not query.calls
