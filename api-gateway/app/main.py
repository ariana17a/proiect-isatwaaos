from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx

app = FastAPI(title="USV API Gateway")

SERVICE_ROUTES: dict[str, str] = {
    "auth": "http://auth-service:8000",
    "users": "http://auth-service:8000",
    "events": "http://events-service:8000",
    "feedback": "http://feedback-service:8000",
    "notifications": "http://notifications-service:8004",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_target(path: str) -> str:
    prefix = path.split("/", 1)[0]
    target_base = SERVICE_ROUTES.get(prefix)
    if not target_base:
        raise HTTPException(status_code=404, detail="Gateway route not found")
    return f"{target_base}/{path}"


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "api-gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy(path: str, request: Request) -> Response:
    target_url = _resolve_target(path)

    forwarded_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            content=await request.body(),
            headers=forwarded_headers,
        )

    excluded = {"content-encoding", "transfer-encoding", "connection"}
    headers = {k: v for k, v in upstream.headers.items() if k.lower() not in excluded}

    return Response(content=upstream.content, status_code=upstream.status_code, headers=headers)
