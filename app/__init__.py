import os
import time
from flask import Flask
from app.config import PublicConfig

def create_app(config=None, *, repository_factory=None, clock=time.monotonic):
    app=Flask(__name__)
    app.config.from_mapping(SUPABASE_URL=os.getenv("SUPABASE_URL"),SUPABASE_PUBLISHABLE_KEY=os.getenv("SUPABASE_PUBLISHABLE_KEY"),PUBLIC_READ_TIMEOUT_SECONDS=os.getenv("PUBLIC_READ_TIMEOUT_SECONDS",6),PUBLIC_DESTINATIONS={})
    app.config.update(config or {})
    if repository_factory is None:
        from app.public.repository import PublicRepository
        repository_factory=lambda:PublicRepository(PublicConfig.from_mapping(app.config),clock=clock)
    app.extensions["public_repository_factory"]=repository_factory
    from app.public.routes import public
    app.register_blueprint(public)
    return app
