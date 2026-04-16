import threading
from fastapi import APIRouter, BackgroundTasks
from typing import Dict, Any

from training.blue_team.training_loop import run_training_battle
from training.training_report import TrainingReport
from training.learning.global_memory import memory

router = APIRouter(prefix="/training", tags=["training"])

# Global state to track status
training_status = {
    "is_running": False,
    "last_report": None,
    "error": None
}

def _run_training_background(episodes: int, strategy: str):
    global training_status
    try:
        training_status["is_running"] = True
        training_status["error"] = None
        report = run_training_battle(n_episodes=episodes, strategy=strategy)
        training_status["last_report"] = report.to_dict()
    except Exception as e:
        training_status["error"] = str(e)
    finally:
        training_status["is_running"] = False

@router.post("/run")
def start_training(background_tasks: BackgroundTasks, payload: Dict[str, Any] = None):
    global training_status
    
    if training_status["is_running"]:
        return {"status": "already_running"}
        
    episodes = 100
    strategy = "random"
    
    if payload:
        episodes = payload.get("episodes", 100)
        strategy = payload.get("strategy", "random")
        
    background_tasks.add_task(_run_training_background, episodes, strategy)
    
    return {"status": "started", "episodes": episodes, "strategy": strategy}

@router.get("/status")
def get_status():
    return training_status

@router.get("/memory")
def get_memory_stats():
    return {
        "size": memory.size(),
        "entries": [
            {
                "action": e.action,
                "score": e.score,
                "executions": e.executions
            }
            for e in memory.get_all()
        ]
    }
