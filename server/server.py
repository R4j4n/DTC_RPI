import uvicorn
from pathlib import Path
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from session_encrypt import auth_manager
from src.hdmi_controllers import CECController
from src.routers.group_router import group_router
from src.routers.inputs_switch import initialize_router_cec_controller, router_cec
from src.routers.tv_controller import initialize_router_tv_controller, tv_router
from src.routers.video_manager import (  # main router
    initialize_router_video_manager,
    initialize_router_video_manager_logger,
    router_main,
)
from src.tv_controller import TVController
from src.utils import register_service
from src.chromium_video_manager import PlayerState, logger, video_manager

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication dependency
async def verify_token(AUTH: str = Header(...)):
    if not auth_manager.verify_api_key(AUTH):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return AUTH


# Pydantic models
class Login(BaseModel):
    password: str


# Routes to add to your FastAPI app
@app.post("/auth/login")
async def login(request: Login):
    """Login and get an API key"""
    api_key = auth_manager.get_api_key(request.password)
    return {"message": "Login successful", "token": api_key}


# Router protection function
def protect_router(router: APIRouter) -> APIRouter:
    """Add authentication to all routes in a router"""
    new_router = APIRouter()

    for route in router.routes:
        dependencies = list(route.dependencies)
        dependencies.append(Depends(verify_token))

        new_router.add_api_route(
            path=route.path,
            endpoint=route.endpoint,
            methods=route.methods,
            dependencies=dependencies,
            name=route.name,
            response_model=route.response_model,
            description=route.description,
        )

    return new_router


# Function to initialize protected routers
def initialize_protected_routers(app: FastAPI, use: bool = False):
    """Initialize all routers with authentication"""
    # Protect TV controller router
    tv_controller = TVController()
    initialize_router_tv_controller(tv_controller)
    if use:
        protected_tv_router = protect_router(tv_router)
        app.include_router(protected_tv_router, prefix="/tv", tags=["Schedule Tv"])
    else:
        app.include_router(tv_router, prefix="/tv", tags=["Schedule Tv"])

    # Protect CEC controller router
    cec_controller = CECController()
    initialize_router_cec_controller(cec_controller)
    if use:
        protected_cec_router = protect_router(router_cec)
        app.include_router(protected_cec_router, prefix="/tv", tags=["CEC commnads"])
    else:
        app.include_router(router_cec, prefix="/tv", tags=["CEC commnads"])

    # # Protect group router
    # if use:
    #     protected_group_router = protect_router(group_router)
    #     app.include_router(protected_group_router, prefix="/groups", tags=["Groups"])
    # else:
    #     app.include_router(group_router, prefix="/groups", tags=["Groups"])

    # Protect main router
    initialize_router_video_manager(video_manager)
    initialize_router_video_manager_logger(logger)
    if use:
        protected_video_manager = protect_router(router_main)
        app.include_router(protected_video_manager, tags=["Main Video Controller"])
    else:
        app.include_router(router_main, tags=["Main Video Controller"])


initialize_protected_routers(app, use=True)


# Mount static files for video serving (no auth required for player)
app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")


# HTML Player endpoint (no auth required)
@app.get("/player", response_class=HTMLResponse)
async def get_player():
    """Serve the HTML video player interface"""
    try:
        html_path = Path("templates/video_player.html")
        if not html_path.exists():
            raise HTTPException(status_code=404, detail="Player template not found")

        with open(html_path, "r") as f:
            html_content = f.read()

        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error serving player: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# API endpoint for player state (no auth required for local browser)
@app.get("/api/player/state")
async def get_player_state():
    """Get current player state for HTML player to consume"""
    try:
        state = video_manager.get_player_state()
        return state
    except Exception as e:
        logger.error(f"Error getting player state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    zeroconf = register_service()
    uvicorn.run(app, host="0.0.0.0", port=8000)
