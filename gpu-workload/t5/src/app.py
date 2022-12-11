#!/usr/bin/env python3

import logging
from fast_dash import FastDash
import requests
from os import environ

logger = logging.getLogger(__name__)

MANAGEMENT_URL = environ.get('MODEL_MANAGEMENT', 'http://localhost:8081/models/t5')
PREDICTION_URL = environ.get('MODEL_PREDICTION', 'http://localhost:8080/predictions/t5/1.0')
GITHUB_URL = environ.get('GITHUB_URL', 'https://github.com/epam/gcp-go2-auto')
DEFAULT_MODELS = ["t5"]
LANG_MAP = {
  "en": "English",
  "fr": "French",
  "de": "German",
  "es": "Spanish",
}

logger.info(f"Model prediction: {PREDICTION_URL}")

def text_to_text_function(text: str, from_lang=LANG_MAP, to_lang=LANG_MAP) -> str:
  headers = {"Content-Type": "application/json"}
  payload = {"text": text, "from": from_lang, "to": to_lang}
  resp = requests.post(PREDICTION_URL, json=payload, headers=headers)
  if resp.status_code == 200:
    content = resp.json()
    return content.get("text")
  else:
    return "Oops, something went wrong!"

app = FastDash(
  callback_fn=text_to_text_function,
  title="T5 model serving",
  github_url=GITHUB_URL,
)

if __name__ == "__main__":
  app.run_server(debug=True, port=8050)
