from itertools import product
import pytest
from bs4 import BeautifulSoup
from conftest import FakeRepository
from app.public.service import ResourceResult

@pytest.mark.parametrize("skills,academic",list(product(["ready","empty","unavailable"],repeat=2)))
def test_independent_collections(make_app,skills,academic):
    repo=FakeRepository(skills=ResourceResult(skills,[dict(name="Capacidad <b>verificada</b>",description=None)] if skills=="ready" else None),academic=ResourceResult(academic,[dict(activity="Actividad",institution=None,start_date=None,end_date=None,ongoing=True,description=None)] if academic=="ready" else None))
    response=make_app(repo).test_client().get("/")
    soup=BeautifulSoup(response.text,"html.parser")
    assert response.status_code==200
    for state,anchor in [(skills,"conocimientos"),(academic,"experiencia-academica")]:
        assert bool(soup.find(id=anchor))==(state!="empty")
        assert bool(soup.find("a",href="#"+anchor))==(state!="empty")
    assert "<b>verificada</b>" not in response.text
    if academic=="ready": assert "Actualidad" in response.text
    assert repo.calls==["profile","skills","academic"]
