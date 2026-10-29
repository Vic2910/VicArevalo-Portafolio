"""Explicit test-only local preview. Never imported by the production factory."""
from app import create_app
from app.public.service import ResourceResult
from flask import request
from conftest import FakeRepository, PROFILE

def repository():
    state=request.args.get("state","ready")
    if state not in ("ready","empty","unavailable"): state="ready"
    skills=request.args.get("skills","ready")
    academic=request.args.get("academic","ready")
    if skills not in ("ready","empty","unavailable"): skills="ready"
    if academic not in ("ready","empty","unavailable"): academic="ready"
    return FakeRepository(
        profile=ResourceResult(state,{**PROFILE,"summary":"Contenido sintético de validación local. No corresponde a afirmaciones reales."} if state=="ready" else None),
        skills=ResourceResult(skills,[dict(name="Capacidad sintética",description="Descripción sintética extensa para comprobar la lectura y distribución del contenido.")] if skills=="ready" else None),
        academic=ResourceResult(academic,[dict(activity="Actividad académica sintética",institution="Institución de prueba",start_date="2026-01-01",end_date=None,ongoing=True,description="Datos exclusivos de prueba.")] if academic=="ready" else None))

app=create_app({"TESTING":True},repository_factory=repository)
if __name__=="__main__": app.run(host="127.0.0.1",port=5051,debug=False)
