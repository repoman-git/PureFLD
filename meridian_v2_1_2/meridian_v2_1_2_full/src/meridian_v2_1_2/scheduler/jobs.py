"""Job Scheduler for Meridian"""
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=22, minute=0)
def daily_pipeline_job():
    """Run daily pipeline at 10 PM"""
    print(f"Running daily pipeline at {datetime.now()}")
    # Import and run pipeline
    from meridian_v2_1_2.pipeline.meridian_pipeline import pipeline
    # pipeline.run(price_data)
    print("Daily pipeline complete")

def start_scheduler():
    """Start job scheduler"""
    print("🚀 Meridian scheduler starting...")
    scheduler.start()

