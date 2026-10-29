import pytest
from app.public.repository import contact,collection_item
from test_profile_repository import ROW

@pytest.mark.parametrize("kind,value,expected",[("email","test@example.test","mailto:test@example.test"),("https","https://example.test/path","https://example.test/path"),("phone","+503 7000-0000","tel:+50370000000")])
def test_contact_links(kind,value,expected):
    assert contact(dict(kind=kind,label="Contacto sintético",value=value))["href"]==expected

@pytest.mark.parametrize("start,end,ongoing",[("2026-02-01","2026-01-01",False),(None,"2026-01-01",True),("2026-13-01",None,False)])
def test_invalid_academic_dates(start,end,ongoing):
    row={**ROW,"profile_id":ROW["id"],"display_order":0,"activity":"Actividad","institution":None,"description":None,"start_date":start,"end_date":end,"ongoing":ongoing}
    with pytest.raises(ValueError): collection_item(row,True,ROW["id"])

def test_preserves_optional_academic_dates():
    row={**ROW,"profile_id":ROW["id"],"display_order":0,"activity":"Actividad","institution":None,"description":None,"start_date":None,"end_date":None,"ongoing":False}
    item=collection_item(row,True,ROW["id"])
    assert item["start_date"] is None and item["end_date"] is None
