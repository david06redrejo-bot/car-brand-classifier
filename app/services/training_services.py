"""
app/services/training_services.py

Facade for TrainingService to match requested API:
services.training_services.retrain_domain
"""

from app.services.training import TrainingService

_trainer = TrainingService()

def retrain_domain(domain: str):
    """
    Triggers retraining for a domain.
    Facades TrainingService.run_async (but handled synchronously or async depending on call).
    The user request background_tasks.add_task(..., retrain_domain, domain=domain).
    BackgroundTasks runs async functions or standard functions in threadpool.
    TrainingService.run_training_job is synchronous.
    TrainingService.run_async is async.
    
    If we alias retrain_domain = _trainer.run_training_job, it runs in threadpool.
    """
    return _trainer.run_training_job(domain=domain)
