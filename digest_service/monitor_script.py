import subprocess
import os
import signal
import time
from shared.db_utils import load_schedule_from_db_sync
from shared.loggers import get_logger
from datetime import datetime

# Configure logging
logger = get_logger('digest-mon.main')

# Start the Celery worker and beat as separate processes
celery_worker_process = subprocess.Popen(
    ["celery", "-A", "digest_service.tasks", "worker", "-Q", "digest_queue", "--loglevel=info"])
celery_beat_process = subprocess.Popen(["celery", "-A", "digest_service.tasks", "beat", "--loglevel=info"])
logger.info("Started Celery worker", pid=celery_worker_process.pid)
logger.info("Started Celery beat", pid=celery_beat_process.pid)


def load_schedule_from_db_sync_with_retry(retries=100, delay=5):
    for i in range(retries):
        try:
            return load_schedule_from_db_sync()
        except Exception as e:
            logger.error(f"Failed to load schedule", error=e)
            if i < retries - 1:  # no delay on the last attempt
                time.sleep(delay)
    logger.error("Failed to load schedule from DB after multiple retries")
    raise Exception("Failed to load schedule from DB after multiple retries")


def restart_celery():
    """
    Restarts the Celery worker and beat
    """
    global celery_worker_process
    global celery_beat_process

    try:
        # Send the SIGTERM signal to the Celery worker process
        logger.info("Sending SIGTERM to Celery worker", pid=celery_worker_process.pid)
        os.kill(celery_worker_process.pid, signal.SIGTERM)

        # Send the SIGTERM signal to the Celery beat process
        logger.info("Sent SIGTERM to Celery beat", pid=celery_beat_process.pid)
        os.kill(celery_beat_process.pid, signal.SIGTERM)


        # Wait for the Celery worker and beat processes to terminate
        celery_worker_process.wait()
        celery_beat_process.wait()
        logger.info("Celery worker and beat have terminated")

        # Start new Celery worker and beat processes
        celery_worker_process = subprocess.Popen(["celery", "-A", "digest_service.tasks", "worker", "-Q", "digest_queue", "--loglevel=info"])
        celery_beat_process = subprocess.Popen(["celery", "-A", "digest_service.tasks", "beat", "--loglevel=info"])
        logger.info(f"Started new Celery worker", pid=celery_worker_process.pid)
        logger.info(f"Started new Celery beat with PID", pid=celery_beat_process.pid)
    except Exception as e:
        logger.error(f"Failed to restart Celery worker and beat", error=e)


def main():
    """
    Main function to monitor changes in the beat schedule and restart Celery worker when needed
    """
    last_seen_schedule = None

    while True:
        now = datetime.now()
        if True:  # Only proceed if the current minute is not between 50 and 58
            current_schedule = load_schedule_from_db_sync_with_retry()
            logger.info(f"Start checking")
            if last_seen_schedule != current_schedule:
                logger.info("Schedule changed, restarting Celery worker")
                restart_celery()
                last_seen_schedule = current_schedule
            else:
                logger.info("No change in schedule detected")
        else:
            logger.info("Not checking for changes due to current time")

        # Sleep for 90 seconds to avoid excessive DB queries
        time.sleep(60)


if __name__ == "__main__":
    main()
