import pytest
from test_profile_repository import repository, ROW

def skill(n):
    return dict(id=f"00000000-0000-4000-8000-{n:012d}",profile_id=ROW["id"],name=f"Capacidad {n}",description=None,display_order=n,published_at="2026-10-27T00:00:00Z")

def test_full_pagination_and_order():
    repo,query=repository([[skill(n) for n in range(100)],[skill(100)]])
    result=repo.list_skills(ROW["id"])
    assert result.state=="ready" and len(result.data)==101
    assert [(args) for name,args,_ in query.calls if name=="range"]==[(0,99),(100,199)]
    assert [args[0] for name,args,_ in query.calls if name=="order"]==["display_order","id"]*2

@pytest.mark.parametrize("responses,state",[([[]],"empty"),([[skill(n) for n in range(100)],RuntimeError("secret")],"unavailable"),([[{}]],"unavailable")])
def test_collection_states(responses,state):
    repo,_=repository(responses)
    result=repo.list_skills(ROW["id"])
    assert result.state==state
    if state!="ready": assert result.data is None

def test_later_page_deadline_discards_partial():
    ticks=iter([0,0,7])
    repo,query=repository([[skill(n) for n in range(100)]],clock=lambda:next(ticks))
    assert repo.list_skills(ROW["id"]).state=="unavailable"
    assert sum(name=="execute" for name,_,_ in query.calls)==1
