from rq import Worker

from app.queue import incident_queue, redis_connection


if __name__ == "__main__":
    worker = Worker(
        [incident_queue],
        connection=redis_connection,
        name="incident-analysis-worker",
    )

    worker.work(with_scheduler=True)
