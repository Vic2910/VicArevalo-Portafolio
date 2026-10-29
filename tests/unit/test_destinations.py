import pytest
from bs4 import BeautifulSoup

@pytest.mark.parametrize("key",["projects","contact","cv"])
@pytest.mark.parametrize("registered",[False,True])
@pytest.mark.parametrize("enabled",[False,True])
def test_destination_matrix(make_app,key,registered,enabled):
    app=make_app(PUBLIC_DESTINATIONS={key:{"endpoint":"test_destination","enabled":enabled,"approved_variant":True}})
    if registered:
        app.add_url_rule("/test-destination", "test_destination",lambda:"Destino aprobado")
    soup=BeautifulSoup(app.test_client().get("/").text,"html.parser")
    element=soup.find(attrs={"data-destination":key})
    assert bool(element.find("a"))==(registered and enabled)
    if registered and enabled:
        assert app.test_client().get(element.a["href"]).text=="Destino aprobado"
    else:
        assert not element.select("[href], [tabindex], button")

def test_cv_requires_approved_variant(make_app):
    app=make_app(PUBLIC_DESTINATIONS={"cv":{"enabled":True,"endpoint":"cv"}})
    app.add_url_rule("/cv","cv",lambda:"CV")
    assert 'href="/cv"' not in app.test_client().get("/").text
