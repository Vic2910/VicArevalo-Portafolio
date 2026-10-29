import pytest
import socket
from app import create_app
from app.public.service import ResourceResult

PROFILE = dict(id="11111111-1111-4111-8111-111111111111", full_name="Persona sintética", degree="Carrera de prueba", summary=None, public_contacts=[])

@pytest.fixture(autouse=True)
def no_network_by_default(request,monkeypatch):
    if request.node.get_closest_marker("rls"):
        return
    def blocked(*args,**kwargs):
        raise AssertionError("Network is disabled for unit/contract tests")
    monkeypatch.setattr(socket.socket,"connect",blocked)

class FakeRepository:
    def __init__(self, profile=None, skills=None, academic=None):
        self.profile = profile if profile is not None else ResourceResult("ready", PROFILE.copy())
        self.skills = skills if skills is not None else ResourceResult("empty")
        self.academic = academic if academic is not None else ResourceResult("empty")
        self.calls = []

    def get_profile(self):
        self.calls.append("profile")
        return self.profile

    def list_skills(self, profile_id):
        self.calls.append("skills")
        return self.skills

    def list_academic_experiences(self, profile_id):
        self.calls.append("academic")
        return self.academic

@pytest.fixture
def make_app():
    return lambda repo=None, **config: create_app({"TESTING": True, **config}, repository_factory=lambda: repo or FakeRepository())
