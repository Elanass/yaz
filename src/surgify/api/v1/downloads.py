"""
App Downloads API - Surgify Platform
Handles mobile and desktop app download requests
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

router = APIRouter(tags=["Downloads"])
logger = logging.getLogger(__name__)

# Download base directory
DOWNLOADS_DIR = Path(__file__).parent.parent / "downloads"


@router.get("/download/desktop")
async def download_desktop_app(request: Request):
    """Download desktop application"""
    try:
        # In production, you would serve the actual .exe/.dmg/.deb file
        # For now, we'll redirect to a GitHub releases page or similar
        logger.info(f"Desktop app download requested from {request.client.host}")

        # You could detect OS from user agent and serve appropriate file
        user_agent = request.headers.get("user-agent", "").lower()

        if "windows" in user_agent:
            # return FileResponse("path/to/surgify-setup.exe")
            return {"message": "Windows desktop app download will be available soon"}
        elif "mac" in user_agent:
            # return FileResponse("path/to/surgify.dmg")
            return {"message": "macOS desktop app download will be available soon"}
        else:
            # return FileResponse("path/to/surgify.deb")
            return {"message": "Linux desktop app download will be available soon"}

    except Exception as e:
        logger.error(f"Desktop download error: {e}")
        raise HTTPException(status_code=500, detail="Download temporarily unavailable")


@router.get("/download/ios")
async def download_ios_app():
    """Redirect to iOS App Store"""
    try:
        logger.info("iOS app download requested")
        # In production, redirect to actual App Store URL
        app_store_url = "https://apps.apple.com/app/surgify"  # Replace with actual URL
        return {
            "message": "iOS app will be available on the App Store soon",
            "url": app_store_url,
        }
    except Exception as e:
        logger.error(f"iOS download error: {e}")
        raise HTTPException(
            status_code=500, detail="App Store link temporarily unavailable"
        )


@router.get("/download/android")
async def download_android_app():
    """Redirect to Google Play Store"""
    try:
        logger.info("Android app download requested")
        # In production, redirect to actual Play Store URL
        play_store_url = "https://play.google.com/store/apps/details?id=com.surgify.app"  # Replace with actual URL
        return {
            "message": "Android app will be available on Google Play soon",
            "url": play_store_url,
        }
    except Exception as e:
        logger.error(f"Android download error: {e}")
        raise HTTPException(
            status_code=500, detail="Play Store link temporarily unavailable"
        )


@router.get("/download/info")
async def get_download_info():
    """Get information about available downloads"""
    return {
        "desktop": {
            "platforms": ["Windows", "macOS", "Linux"],
            "status": "In Development",
            "size": "~150MB",
            "version": "1.0.0-beta",
        },
        "ios": {
            "platforms": ["iPhone", "iPad"],
            "status": "Planned",
            "min_version": "iOS 14.0+",
            "version": "1.0.0",
        },
        "android": {
            "platforms": ["Android"],
            "status": "Planned",
            "min_version": "Android 8.0+ (API 26)",
            "version": "1.0.0",
        },
    }
