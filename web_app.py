import json
from pathlib import Path
from aiohttp import web
from config import BELLS, DAYS_RU
from scheduler import SCHEDULE, get_status

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"


@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


async def index_handler(request: web.Request) -> web.Response:
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return web.Response(text="Mini App HTML not found", status=404)
    return web.FileResponse(index_file)


def _json_response(data: dict) -> web.Response:
    return web.json_response(data, dumps=lambda obj: json.dumps(obj, ensure_ascii=False))


async def api_schedule(request: web.Request) -> web.Response:
    data = {
        "days": SCHEDULE,
        "days_ru": DAYS_RU,
        "days_order": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    }
    return _json_response(data)


async def api_bells(request: web.Request) -> web.Response:
    formatted_bells = [
        {"name": name, "start": start, "end": end}
        for name, start, end in BELLS
    ]
    return _json_response({"bells": formatted_bells})


async def api_status(request: web.Request) -> web.Response:
    return _json_response(get_status())



def setup_web_app(app: web.Application) -> None:
    app.middlewares.append(cors_middleware)
    app.router.add_get("/", index_handler)
    app.router.add_get("/api/schedule", api_schedule)
    app.router.add_get("/api/bells", api_bells)
    app.router.add_get("/api/status", api_status)

    if STATIC_DIR.exists():
        app.router.add_static("/static/", path=STATIC_DIR, name="static")
