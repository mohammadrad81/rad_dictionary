import os
from random import random

import requests
import json
from flask import Flask, request
from redis import Redis
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='rad_dictionary.log', encoding='utf-8', level=logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# load_dotenv()
SERVER_PORT = int(os.getenv("SERVER_PORT"))
CACHING_TIME = int(os.getenv("CACHING_TIME"))
API_KEY = os.getenv("API_KEY")
RANDOM_WORD_SERVICE = os.getenv("RANDOM_WORD_SERVICE")
WORD_MEANING_SERVICE = os.getenv("WORD_MEANING_SERVICE")
REDIS_CACHE_IP = os.getenv("REDIS_CACHE_IP")
REDIS_CACHE_PORT = int(os.getenv("REDIS_CACHE_PORT"))
print(REDIS_CACHE_IP)
print(REDIS_CACHE_PORT)

app = Flask(__name__)
cache = Redis(REDIS_CACHE_IP, REDIS_CACHE_PORT)
# just a random comment
def get_random_word() -> str:
    headers = {
        "x-api-key": API_KEY
    }
    logger.info("before sending request to receive random word.")
    result = requests.get(RANDOM_WORD_SERVICE, headers=headers)
    logger.info("random word received")
    word = json.loads(result.content.decode())["word"][0]
    return word

def get_meaning_of_word(word: str) -> tuple[str, bool]:
    logger.info("before checking cache for word")
    cached_value = cache.get(word)
    logger.info("after checking cache for word")
    if cached_value is not None:
        logger.info("word was in cache")
        return cached_value.decode(), True
    headers = {
        "x-api-key": API_KEY
    }
    params = {
        "word": word
    }
    logger.info("before getting the meaning of the word")
    result = requests.get(WORD_MEANING_SERVICE, headers=headers, params=params)
    logger.info("after getting the meaning of the word")
    meaning = json.loads(result.content.decode())["definition"]
    cache.set(word, meaning, ex=CACHING_TIME)
    return meaning, False

@app.route("/")
def liveness():
    logger.info("liveness called.")
    return {"message": "server is up."}

@app.route("/meaning/")
def meaning_of_word():
    word = request.args.get("word")
    logger.info("meaning_of_word_called")
    meaning, from_cache = get_meaning_of_word(word)
    result = {
        "word": word,
        "meaning": meaning,
        "from_cache": from_cache
    }
    return result

@app.route("/random-word-with-meaning/")
def random_word_with_meaning():
    random_word = get_random_word()
    meaning, from_cache = get_meaning_of_word(random_word)
    result = {
        "random_word": random_word,
        "meaning": meaning,
        "from_cache": from_cache
    }
    return result

if __name__ == "__main__":
    app.run("0.0.0.0", SERVER_PORT)