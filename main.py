import os
import requests
from flask import Flask
from redis import Redis
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='rad_dictionary.log', encoding='utf-8', level=logging.DEBUG)

load_dotenv()
SERVER_PORT = os.getenv("SERVER_PORT")
CACHING_TIME = os.getenv("CACHING_TIME")
API_KEY = os.getenv("API_KEY")
RANDOM_WORD_SERVICE = os.getenv("RANDOM_WORD_SERVICE")
WORD_MEANING_SERVICE = os.getenv("WORD_MEANING_SERVICE")

app = Flask(__name__)

@app.route("/")
def liveness():
    logger.info("liveness called.")
    return {"message": "server is up."}


if __name__ == "__main__":
    app.run("0.0.0.0", SERVER_PORT)