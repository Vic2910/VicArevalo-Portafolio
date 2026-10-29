from dataclasses import dataclass
from flask import current_app, url_for
from werkzeug.routing import BuildError

@dataclass(frozen=True)
class ResourceResult:
    state: str
    data: object = None
    error: str | None = None

    def __post_init__(self):
        if self.state not in ("ready","empty","unavailable"): raise ValueError("Invalid resource state")
        if (self.state=="ready") != (self.data is not None): raise ValueError("Data requires ready state")
        if self.error not in (None,"configuration","timeout","http","invalid","unavailable"): raise ValueError("Invalid error category")

@dataclass(frozen=True)
class Destination:
    key: str
    label: str
    url: str | None = None

    @property
    def available(self): return self.url is not None

@dataclass(frozen=True)
class PublicPage:
    profile: ResourceResult
    skills: ResourceResult
    academic: ResourceResult
    destinations: list[Destination]

def destinations():
    settings=current_app.config.get("PUBLIC_DESTINATIONS",{})
    result=[]
    for key,label in (("projects","Proyectos"),("contact","Contacto"),("cv","CV")):
        config=settings.get(key,{})
        endpoint=config.get("endpoint")
        url=None
        if config.get("enabled") is True and endpoint in current_app.view_functions and (key!="cv" or config.get("approved_variant") is True):
            try:
                candidate=url_for(endpoint,**config.get("values",{}))
                if candidate.startswith("/") and not candidate.startswith("//"): url=candidate
            except BuildError:
                pass
        result.append(Destination(key,label,url))
    return result

def build_page(repository):
    profile=repository.get_profile()
    skills=academic=ResourceResult("empty")
    if profile.state=="ready":
        skills=repository.list_skills(profile.data["id"])
        academic=repository.list_academic_experiences(profile.data["id"])
    return PublicPage(profile,skills,academic,destinations())
