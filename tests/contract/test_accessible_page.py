import pytest
from bs4 import BeautifulSoup
from conftest import FakeRepository, PROFILE
from app.public.service import ResourceResult

@pytest.mark.parametrize("state",["ready","empty","unavailable"])
def test_semantics(make_app,state):
    repo=FakeRepository(profile=ResourceResult(state,PROFILE if state=="ready" else None))
    soup=BeautifulSoup(make_app(repo).test_client().get("/").text,"html.parser")
    assert soup.html["lang"]=="es"
    assert soup.title.text.strip()
    assert len(soup.find_all("h1"))==1
    for region in ["header","nav","main","footer"]:
        assert soup.find(region)
    assert soup.select_one('a[href="#contenido"]')
    for anchor in soup.select('a[href^="#"]'):
        assert soup.find(id=anchor["href"][1:])
    assert not soup.find("script")
