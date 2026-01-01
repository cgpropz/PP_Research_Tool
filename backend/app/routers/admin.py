"""
Admin API Endpoints
Manage data refresh and system status
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Optional

from ..refresh_service import refresh_service
from ..data_service import data_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status")
async def get_system_status():
    """Get full system status"""
    return {
        'data_files': data_service.get_data_status(),
        'refresh_service': refresh_service.get_status(),
    }


@router.post("/refresh/fetch/{script_name}")
async def run_fetch_script(script_name: str, background_tasks: BackgroundTasks):
    """Run a fetch script to update external data"""
    valid_scripts = ['schedule', 'injuries', 'gamelogs', 'pp_odds']
    if script_name not in valid_scripts:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid script. Valid options: {valid_scripts}"
        )
    
    # Run in background
    background_tasks.add_task(refresh_service.run_fetch_script, script_name)
    return {"message": f"Started fetch script: {script_name}", "status": "running"}


@router.post("/refresh/build/{script_name}")
async def run_build_script(script_name: str, background_tasks: BackgroundTasks):
    """Run a build script to process data"""
    valid_scripts = ['gamelogs_json', 'ui_cards', 'add_score', 'add_player_id']
    if script_name not in valid_scripts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid script. Valid options: {valid_scripts}"
        )
    
    # Run in background
    background_tasks.add_task(refresh_service.run_build_script, script_name)
    return {"message": f"Started build script: {script_name}", "status": "running"}


@router.post("/refresh/all")
async def run_full_refresh(background_tasks: BackgroundTasks):
    """Run full data refresh pipeline"""
    background_tasks.add_task(refresh_service.run_full_refresh)
    return {"message": "Started full refresh", "status": "running"}


@router.post("/cache/clear")
async def clear_cache(key: Optional[str] = None):
    """Clear data cache"""
    data_service.clear_cache(key)
    return {"message": f"Cache cleared: {key or 'all'}"}


@router.get("/scripts")
async def list_scripts():
    """List all available scripts"""
    status = refresh_service.get_status()
    return {
        'fetch_scripts': list(status['fetch_scripts'].keys()),
        'build_scripts': list(status['build_scripts'].keys()),
    }
