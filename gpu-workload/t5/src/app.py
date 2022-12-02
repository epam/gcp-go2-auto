#!/usr/bin/env python3

import logging
from fast_dash import FastDash
import requests
from os import environ

logger = logging.getLogger(__name__)

PREDICTION_URL = environ.get('MODEL_URL', 'http://localhost:8080/predictions/t5-large/1.0')
LANG_MAP = {
  "en": "English",
  "fr": "French",
  "de": "German",
  "es": "Spanish",
}

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
  update_live=False,
)

if __name__ == "__main__":
  app.run_server(debug=True, port=8050)

