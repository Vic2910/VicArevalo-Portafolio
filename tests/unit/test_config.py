import base64
import json
import pytest
from app.config import PublicConfig

@pytest.mark.parametrize("key",[None,"sb_secret_private","service_role","invalid","sb_publishable_test\n"])
def test_privileged_or_invalid_key_rejected(key):
    assert not PublicConfig("https://example.supabase.co",key).valid

@pytest.mark.parametrize("role,valid",[("anon",True),("service_role",False),("authenticated",False)])
def test_legacy_role(role,valid):
    payload=base64.urlsafe_b64encode(json.dumps({"role":role}).encode()).decode().rstrip("=")
    assert PublicConfig("https://example.supabase.co","header."+payload+".signature").valid is valid

@pytest.mark.parametrize("url",["https://user:password@example.com","https://example.com?key=secret","file:///etc/passwd","http://example.com"])
def test_invalid_url(url):
    assert not PublicConfig(url,"sb_publishable_test").valid
