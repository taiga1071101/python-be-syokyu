import os
from fastapi import FastAPI
from .routers import list_router, item_router

from fastapi.routing import APIRoute

DEBUG = os.environ.get("DEBUG", "") == "true"

app = FastAPI(
    title="Python Backend Stations",
    debug=DEBUG,
)

if DEBUG:
    from debug_toolbar.middleware import DebugToolbarMiddleware

    # panelsに追加で表示するパネルを指定できる
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=["app.database.SQLAlchemyPanel"],
    )

app.include_router(list_router.router)
app.include_router(item_router.router)

for route in app.routes:
    print(route.path, route.methods)