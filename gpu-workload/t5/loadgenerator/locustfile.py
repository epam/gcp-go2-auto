import os

from locust import FastHttpUser, between, task


class T5User(FastHttpUser):
    wait_time = between(2.0, 2.5)

    def on_start(self):
        model_name = os.getenv('MODEL_NAME', 't5-small')
        model_version = os.getenv('MODEL_VERSION', '1.0')

        self.infer_url = f'{self.environment.host}/predictions/{model_name}/{model_version}'
        self.payload = {
            "text": "this is a test sentence",
            "from": "en",
            "to": "es"
        }

    @task()
    def t5(self):
        with self.rest('POST', self.infer_url, json=self.payload, stream=False) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(response.js)
