import logging
import os

from dotenv import load_dotenv, find_dotenv

# enable logging (useful in future)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

ENV = bool(os.path.exists(find_dotenv()))

load_dotenv(find_dotenv())

if ENV:
    TOKEN = os.environ.get("TOKEN", None)
    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", None))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")

else:
    LOGGER.info(".env file missing!")