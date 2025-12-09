import atexit
import signal
import sys
import logging

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
from src.video_manager import PlayerState, logger, video_manager
from src.config import ServerConfig

# Setup logging
logging.basicConfig(
    level=getattr(logging, ServerConfig.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
server_logger = logging.getLogger(__name__)

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


# Global cleanup tracker
_zeroconf_service = None
_tv_controller_instance = None


def cleanup_resources():
    """Cleanup resources on shutdown"""
    server_logger.info("Starting graceful shutdown...")

    try:
        # Stop video playback
        if video_manager and video_manager.current_video:
            server_logger.info("Stopping video playback...")
            try:
                video_manager.stop()
            except Exception as e:
                server_logger.error(f"Error stopping video: {e}")

        # Save current state
        if video_manager:
            server_logger.info("Saving last played video...")
            try:
                video_manager.save_last_played()
            except Exception as e:
                server_logger.error(f"Error saving last played: {e}")

        # Cleanup Zeroconf service
        if _zeroconf_service:
            server_logger.info("Unregistering Zeroconf service...")
            try:
                _zeroconf_service.unregister_all_services()
                _zeroconf_service.close()
            except Exception as e:
                server_logger.error(f"Error closing Zeroconf: {e}")

        server_logger.info("Graceful shutdown complete")

    except Exception as e:
        server_logger.error(f"Error during cleanup: {e}")


def signal_handler(signum, frame):
    """Handle termination signals"""
    server_logger.info(f"Received signal {signum}, shutting down...")
    cleanup_resources()
    sys.exit(0)


# Register cleanup handlers
atexit.register(cleanup_resources)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    try:
        server_logger.info("Starting DTC_RPI Server...")
        server_logger.info(f"Configuration: {ServerConfig.get_config_summary()}")

        # Register Zeroconf service
        _zeroconf_service = register_service()

        # Start server with config
        server_logger.info(f"Server listening on {ServerConfig.HOST}:{ServerConfig.PORT}")
        uvicorn.run(app, host=ServerConfig.HOST, port=ServerConfig.PORT)

    except KeyboardInterrupt:
        server_logger.info("Keyboard interrupt received")
        cleanup_resources()
    except Exception as e:
        server_logger.error(f"Server error: {e}")
        cleanup_resources()
        raise
