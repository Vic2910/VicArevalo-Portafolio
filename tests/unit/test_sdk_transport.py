import httpx
import pytest
from supabase import create_client, ClientOptions
from app.public.repository import PublicRepository
from app.config import PublicConfig
from test_profile_repository import ROW

@pytest.mark.parametrize("status,state",[(200,"ready"),(429,"unavailable"),(500,"unavailable"),(401,"unavailable"),(503,"unavailable"),(520,"unavailable")])
def test_real_sdk_queries_without_network(status,state):
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(status,json=[ROW] if status==200 else {"message":"PRIVATE_PROVIDER_SENTINEL"})
    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        config=PublicConfig("https://test.supabase.co","sb_publishable_test")
        sdk=create_client(config.url,config.key,ClientOptions(httpx_client=http,persist_session=False,auto_refresh_token=False))
        repo=PublicRepository(config,client_factory=lambda remaining:sdk)
        result=repo.get_profile()
        assert result.state==state
        assert len(calls)==1
        assert calls[0].method=="GET"
        assert calls[0].url.params["published_at"]=="not.is.null"
        assert "*" not in calls[0].url.params["select"]
        assert "PRIVATE_PROVIDER_SENTINEL" not in repr(result)
