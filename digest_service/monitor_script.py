import subprocess
import os
import signal
import time
import logging
from shared.db_utils import load_schedule_from_db_sync
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Start the Celery worker and beat as separate processes
celery_worker_process = subprocess.Popen(
    ["celery", "-A", "digest_service.tasks", "worker", "-Q", "digest_queue", "--loglevel=info"])
celery_beat_process = subprocess.Popen(["celery", "-A", "digest_service.tasks", "beat", "--loglevel=info"])
logging.info(f"Started Celery worker with PID {celery_worker_process.pid}")
logging.info(f"Started Celery beat with PID {celery_beat_process.pid}")


def load_schedule_from_db_sync_with_retry(retries=100, delay=5):
    for i in range(retries):
        try:
            return load_schedule_from_db_sync()
        except Exception as e:
            logging.error(f"Failed to load schedule from DB: {e}")
            if i < retries - 1:  # no delay on the last attempt
                time.sleep(delay)
    logging.error("Failed to load schedule from DB after multiple retries")
    raise Exception("Failed to load schedule from DB after multiple retries")


def restart_celery():
    """
    Restarts the Celery worker and beat
    """
    global celery_worker_process
    global celery_beat_process

    try:
        # Send the SIGTERM signal to the Celery worker process
        os.kill(celery_worker_process.pid, signal.SIGTERM)
        logging.info("Sent SIGTERM to Celery worker")

        # Send the SIGTERM signal to the Celery beat process
        os.kill(celery_beat_process.pid, signal.SIGTERM)
        logging.info("Sent SIGTERM to Celery beat")

        # Wait for the Celery worker and beat processes to terminate
        celery_worker_process.wait()
        celery_beat_process.wait()
        logging.info("Celery worker and beat have terminated")

        # Start new Celery worker and beat processes
        celery_worker_process = subprocess.Popen(["celery", "-A", "digest_service.tasks", "worker", "-Q", "digest_queue", "--loglevel=info"])
        celery_beat_process = subprocess.Popen(["celery", "-A", "digest_service.tasks", "beat", "--loglevel=info"])
        logging.info(f"Started new Celery worker with PID {celery_worker_process.pid}")
        logging.info(f"Started new Celery beat with PID {celery_beat_process.pid}")
    except Exception as e:
        logging.error(f"Failed to restart Celery worker and beat: {e}")


def main():
    """
    Main function to monitor changes in the beat schedule and restart Celery worker when needed
    """
    last_seen_schedule = None

    while True:
        now = datetime.now()
        if True:  # Only proceed if the current minute is not between 50 and 58
            current_schedule = load_schedule_from_db_sync_with_retry()
            logging.info(f"Start checking")
            if last_seen_schedule != current_schedule:
                logging.info("Schedule changed, restarting Celery worker...")
                restart_celery()
                last_seen_schedule = current_schedule
            else:
                logging.info("No change in schedule detected")
        else:
            logging.info("Not checking for changes due to current time")

        # Sleep for 90 seconds to avoid excessive DB queries
        time.sleep(60)


if __name__ == "__main__":
    main()
