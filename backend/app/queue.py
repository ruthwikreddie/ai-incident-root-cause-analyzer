import os

from dotenv import load_dotenv
from redis import Redis
from rq import Queue


load_dotenv()

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

redis_connection = Redis.from_url(
    REDIS_URL,
    decode_responses=False,
)

incident_queue = Queue(
    "incident-analysis",
    connection=redis_connection,
    default_timeout=120,
)
