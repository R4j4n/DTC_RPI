import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
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
from src.routers.wristband_router import wristband_router
from src.tv_controller import TVController
from src.utils import register_service
from config import config, VideoPlayerMode

# Import appropriate video manager based on configuration
if config.VIDEO_PLAYER_MODE == VideoPlayerMode.WEB:
    from src.web_video_manager import web_video_manager as video_manager, PlayerState, logger
else:
    from src.video_manager import video_manager, PlayerState, logger

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

    # Add wristband schedule router (no auth needed for display)
    app.include_router(wristband_router, prefix="/wristband", tags=["Wristband Schedule"])


initialize_protected_routers(app, use=True)

# Serve static files for kiosk display
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Add route to serve kiosk display
@app.get("/kiosk")
async def serve_kiosk():
    """Serve the kiosk display HTML"""
    kiosk_file = Path(__file__).parent / "static" / "kiosk.html"
    if kiosk_file.exists():
        return FileResponse(kiosk_file)
    raise HTTPException(status_code=404, detail="Kiosk display not found")


# Public endpoints for kiosk (no authentication required)
@app.get("/public/status")
async def get_public_status():
    """Get video player status - public endpoint for kiosk display"""
    status = video_manager.get_status()
    videos = list(video_manager.upload_dir.glob("*.mp4"))

    return {
        "current_video": status["current_video"],
        "is_playing": status["is_playing"],
        "is_paused": status["status"] == PlayerState.PAUSED,
        "is_looping": status["is_looping"],
        "available_videos": [f.name for f in videos],
    }


@app.get("/public/stream/current")
async def stream_current_video_public():
    """Stream the currently loaded video - public endpoint for kiosk display"""
    from fastapi.responses import StreamingResponse

    try:
        status = video_manager.get_status()
        if not status.get("current_video"):
            raise HTTPException(status_code=404, detail="No video currently loaded")

        video_name = status["current_video"]
        video_path = video_manager.upload_dir / video_name

        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Current video file not found")

        def iterfile():
            with open(video_path, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(iterfile(), media_type="video/mp4")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming current video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Print configuration
    print(f"Starting DTC_RPI Server in {config.VIDEO_PLAYER_MODE.value.upper()} mode")

    # Register service for network discovery
    zeroconf = register_service()

    # Auto-launch kiosk if configured and in web mode
    if config.VIDEO_PLAYER_MODE == VideoPlayerMode.WEB and config.KIOSK_AUTO_LAUNCH:
        # Import here to avoid circular dependency
        import threading
        import time

        def delayed_kiosk_launch():
            time.sleep(3)  # Wait for server to start
            print("Launching kiosk display...")
            video_manager.launch_kiosk()

        kiosk_thread = threading.Thread(target=delayed_kiosk_launch, daemon=True)
        kiosk_thread.start()

    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
