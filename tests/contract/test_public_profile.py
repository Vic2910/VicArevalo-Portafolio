import pytest
from conftest import FakeRepository, PROFILE
from app.public.service import ResourceResult

@pytest.mark.parametrize("state,status,message", [("ready",200,"Persona sintética"),("empty",200,"Perfil aún no disponible"),("unavailable",503,"No podemos mostrar el perfil en este momento. Inténtalo más tarde.")])
def test_profile_states(make_app,state,status,message):
    repo=FakeRepository(profile=ResourceResult(state, PROFILE if state=="ready" else None))
    response=make_app(repo).test_client().get("/")
    assert response.status_code==status
    assert message in response.text
    assert response.headers["Cache-Control"]=="no-store"
    assert "charset=utf-8" in response.content_type
    if state!="ready":
        assert repo.calls==["profile"]
        assert "Persona sintética" not in response.text

def test_escape_and_private_omission(make_app):
    data={**PROFILE,"summary":"<script>alert(1)</script>","private":"PRIVATE_SENTINEL"}
    html=make_app(FakeRepository(profile=ResourceResult("ready",data))).test_client().get("/").text
    assert "&lt;script&gt;" in html
    assert "PRIVATE_SENTINEL" not in html
    assert "<script>" not in html
