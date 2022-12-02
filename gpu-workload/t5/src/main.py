#!/usr/bin/env python3

import logging
from fast_dash import FastDash
from transformers import T5Tokenizer, AutoTokenizer
# import transformers

logger = logging.getLogger(__name__)

def text_to_text_function(text: str = "book text", question: str = "text of a question") -> str:
    return "Lorem ipsum!"

app = FastDash(
  callback_fn=text_to_text_function,
  title="Closed Book Question Answering",
  update_live=False,
)

# if __name__ == "__main__":
  # logger.info(f"Transformers version {transformers.__version__}")
  # app.run_server(debug=True, port=8050)
