import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from session_encrypt import auth_manager
from src.hdmi_controllers import CECController
from src.routers.group_router import group_router
from src.routers.inputs_switch import initialize_router_cec_controller, router_cec
from src.routers.tv_controller import initialize_router_tv_controller, tv_router
from src.routers.video_manager import (
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

# Mount static directories
app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")


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


# Serve the HTML video player
@app.get("/player")
async def get_player():
    """Serve the HTML5 video player interface"""
    player_path = Path("web/video_player.html")
    if not player_path.exists():
        raise HTTPException(status_code=404, detail="Video player not found")
    return FileResponse(player_path)


# WebSocket endpoint for video control
@app.websocket("/ws/video")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for bi-directional communication with the video player"""
    await websocket.accept()
    await video_manager.register_websocket(websocket)

    try:
        while True:
            # Receive messages from the browser
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "status":
                # Update player status from browser
                status_data = data.get("data", {})
                video_manager.update_player_status(status_data)
                logger.debug(f"Updated player status: {status_data}")

            elif message_type == "error":
                # Log errors from the browser
                error_msg = data.get("data", {}).get("message", "Unknown error")
                logger.error(f"Browser error: {error_msg}")
                video_manager.error_count += 1

            else:
                logger.warning(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await video_manager.unregister_websocket(websocket)


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

    # Protect main router
    initialize_router_video_manager(video_manager)
    initialize_router_video_manager_logger(logger)
    if use:
        protected_video_manager = protect_router(router_main)
        app.include_router(protected_video_manager, tags=["Main Video Controller"])
    else:
        app.include_router(router_main, tags=["Main Video Controller"])


initialize_protected_routers(app, use=True)


if __name__ == "__main__":
    zeroconf = register_service()
    uvicorn.run(app, host="0.0.0.0", port=8000)
