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

load_dotenv()
SERVER_PORT = os.getenv("SERVER_PORT")
CACHING_TIME = os.getenv("CACHING_TIME")
API_KEY = os.getenv("API_KEY")
RANDOM_WORD_SERVICE = os.getenv("RANDOM_WORD_SERVICE")
WORD_MEANING_SERVICE = os.getenv("WORD_MEANING_SERVICE")
REDIS_CACHE_IP = os.getenv("REDIS_CACHE_IP")
REDIS_CACHE_PORT = os.getenv("REDIS_CACHE_PORT")
print(REDIS_CACHE_IP)
print(REDIS_CACHE_PORT)

app = Flask(__name__)
cache = Redis(REDIS_CACHE_IP, REDIS_CACHE_PORT)

def get_random_word() -> str:
    headers = {
        "x-api-key": API_KEY
    }
    result = requests.get(RANDOM_WORD_SERVICE, headers=headers)
    word = json.loads(result.content.decode())["word"][0]
    return word

def get_meaning_of_word(word: str) -> tuple[str, bool]:
    cached_value = cache.get(word)
    if cached_value is not None:
        return cached_value.decode(), True
    headers = {
        "x-api-key": API_KEY
    }
    params = {
        "word": word
    }
    result = requests.get(WORD_MEANING_SERVICE, headers=headers, params=params)
    meaning = json.loads(result.content.decode())["definition"]
    cache.set(word, meaning)
    return meaning, False

@app.route("/")
def liveness():
    logger.info("liveness called.")
    return {"message": "server is up."}

@app.route("/meaning/")
def meaning_of_word():
    word = request.args.get("word")
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