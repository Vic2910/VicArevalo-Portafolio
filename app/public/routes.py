from flask import Blueprint, current_app, render_template, make_response
from app.public.service import build_page

public=Blueprint("public",__name__)

@public.get("/")
def index():
    repository=current_app.extensions["public_repository_factory"]()
    try:
        page=build_page(repository)
    finally:
        if hasattr(repository,"close"): repository.close()
    response=make_response(render_template("public/index.html",page=page),503 if page.profile.state=="unavailable" else 200)
    response.headers["Cache-Control"]="no-store"
    return response
