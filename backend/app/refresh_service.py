"""
Data Refresh Service
Runs Python fetch scripts to update data files
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading
import json

# Base path for the project
BASE_PATH = Path(__file__).parent.parent.parent

# Scripts that fetch external data
FETCH_SCRIPTS = {
    'schedule': {
        'script': 'fetch_nba_schedule.py',
        'output': 'nba_schedule.json',
        'description': 'Fetch NBA game schedule',
    },
    'injuries': {
        'script': 'fetch_nba_injuries.py',
        'output': 'nba_injuries.json',
        'description': 'Fetch current injury report',
    },
    'gamelogs': {
        'script': 'Fetch_Gamelogs.py',
        'output': 'Full_Gamelogs25.csv',
        'description': 'Fetch player game logs',
    },
    'pp_odds': {
        'script': 'Fetch_PP_Odds.py',
        'output': 'NBA_PURE_STANDARD_SINGLE.json',
        'description': 'Fetch PrizePicks odds lines',
    },
}

# Scripts that process/build data
BUILD_SCRIPTS = {
    'update_all': {
        'script': 'update_all_cards.py',
        'output': 'PLAYER_UI_CARDS_PERFECT.json',
        'description': 'Full update: fetch odds and rebuild all cards',
    },
    'gamelogs_json': {
        'script': 'Gamelogs.py',
        'output': 'Player_Gamelogs25.json',
        'description': 'Convert gamelogs CSV to JSON',
    },
    'ui_cards': {
        'script': 'UI_DATA_BUILDER_PERFECT.py',
        'output': 'PLAYER_UI_CARDS_PERFECT.json',
        'description': 'Build player UI cards from props lines',
    },
    'add_score': {
        'script': 'add_score_to_cards.py',
        'output': 'PLAYER_UI_CARDS_PERFECT.json',
        'description': 'Add scores to player cards',
    },
    'add_player_id': {
        'script': 'add_player_id_to_cards.py',
        'output': 'PLAYER_UI_CARDS_PERFECT.json',
        'description': 'Add player IDs to cards',
    },
}

class DataRefreshService:
    def __init__(self):
        self._running: Dict[str, bool] = {}
        self._last_run: Dict[str, datetime] = {}
        self._last_result: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def _get_python_path(self) -> str:
        """Get the Python interpreter path"""
        # Try to use the venv if available
        venv_python = BASE_PATH / 'backend' / 'venv' / 'bin' / 'python'
        if venv_python.exists():
            return str(venv_python)
        return sys.executable
    
    def _run_script(self, script_name: str, script_info: Dict) -> Dict:
        """Run a Python script and return result"""
        script_path = BASE_PATH / script_info['script']
        
        if not script_path.exists():
            return {
                'success': False,
                'error': f"Script not found: {script_info['script']}",
                'script': script_info['script'],
            }
        
        try:
            python_path = self._get_python_path()
            result = subprocess.run(
                [python_path, str(script_path)],
                cwd=str(BASE_PATH),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'script': script_info['script'],
                'output': result.stdout[-1000:] if result.stdout else '',  # Last 1000 chars
                'error': result.stderr[-500:] if result.stderr else '',
                'return_code': result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Script timed out (5 minutes)',
                'script': script_info['script'],
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'script': script_info['script'],
            }
    
    def run_fetch_script(self, name: str) -> Dict:
        """Run a fetch script by name"""
        if name not in FETCH_SCRIPTS:
            return {'success': False, 'error': f'Unknown fetch script: {name}'}
        
        with self._lock:
            if self._running.get(name):
                return {'success': False, 'error': f'{name} is already running'}
            self._running[name] = True
        
        try:
            result = self._run_script(name, FETCH_SCRIPTS[name])
            with self._lock:
                self._last_run[name] = datetime.now()
                self._last_result[name] = result
            return result
        finally:
            with self._lock:
                self._running[name] = False
    
    def run_build_script(self, name: str) -> Dict:
        """Run a build script by name"""
        if name not in BUILD_SCRIPTS:
            return {'success': False, 'error': f'Unknown build script: {name}'}
        
        key = f'build_{name}'
        with self._lock:
            if self._running.get(key):
                return {'success': False, 'error': f'{name} is already running'}
            self._running[key] = True
        
        try:
            result = self._run_script(name, BUILD_SCRIPTS[name])
            with self._lock:
                self._last_run[key] = datetime.now()
                self._last_result[key] = result
            return result
        finally:
            with self._lock:
                self._running[key] = False
    
    def run_full_refresh(self) -> Dict:
        """Run full data refresh pipeline"""
        results = {
            'fetch': {},
            'build': {},
            'started_at': datetime.now().isoformat(),
        }
        
        # Step 1: Fetch external data
        for name in ['schedule', 'injuries']:
            results['fetch'][name] = self.run_fetch_script(name)
        
        # Step 2: Build derived data
        for name in ['gamelogs_json', 'ui_cards', 'add_score']:
            results['build'][name] = self.run_build_script(name)
        
        results['completed_at'] = datetime.now().isoformat()
        return results
    
    def get_status(self) -> Dict:
        """Get current status of all scripts"""
        status = {
            'fetch_scripts': {},
            'build_scripts': {},
        }
        
        for name, info in FETCH_SCRIPTS.items():
            status['fetch_scripts'][name] = {
                'description': info['description'],
                'output': info['output'],
                'running': self._running.get(name, False),
                'last_run': self._last_run.get(name, None),
                'last_result': self._last_result.get(name),
            }
            if status['fetch_scripts'][name]['last_run']:
                status['fetch_scripts'][name]['last_run'] = status['fetch_scripts'][name]['last_run'].isoformat()
        
        for name, info in BUILD_SCRIPTS.items():
            key = f'build_{name}'
            status['build_scripts'][name] = {
                'description': info['description'],
                'output': info['output'],
                'running': self._running.get(key, False),
                'last_run': self._last_run.get(key),
                'last_result': self._last_result.get(key),
            }
            if status['build_scripts'][name]['last_run']:
                status['build_scripts'][name]['last_run'] = status['build_scripts'][name]['last_run'].isoformat()
        
        return status


# Global singleton
refresh_service = DataRefreshService()
