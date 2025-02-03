import time
from pathlib import Path
from typing import Dict, List

import openai
from openai import OpenAI
from src.configs.config import ModelConfig
from src.keys import OPENAI_API_KEY, OPENAI_ORG_ID
from src.utils.helpers import encode_image

from .api_model import ApiModel


class OpenAIVLM(ApiModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.config = config
        self.client = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORG_ID)

        self.params = {
            "model": self.config.model.models_string,
            "max_tokens": self.config.model.max_tokens,
            "temperature": self.config.model.temperature,
        }

    def _predict_call(self, messages: List[Dict]):

        self.params["messages"] = messages

        retries = 0
        while retries < self.config.error_handling.max_retries:
            try:
                result = self.client.chat.completions.create(**self.params)
                return result
            except openai.RateLimitError:
                print("Rate limit error")
                wait = self.config.error_handling.backoff_factor * (2**retries)
                time.sleep(wait)
                retries += 1
            except openai.OpenAIError as e:
                print(f"Non-rate limit error occurred: {e}")
                wait = self.config.error_handling.backoff_factor * (2**retries)
                time.sleep(wait)
                retries += 1
        return None

    def predict_single(self, image_id: str, attribute: str, **kwargs):
        return super().predict_single(image_id, attribute, **kwargs)

    def predict_multi(self, image_ids: List[str], dataset: List[Dict], **kwargs):
        return super().predict_multi(image_ids, dataset, **kwargs)

    def apply_model_template(
        self, image_id: str, attribute: str, **kwargs
    ) -> List[Dict]:

        image_path = f"{self.config.data.images}/{image_id}.jpg"
        base64_image = encode_image(image_path)

        system_prompt, user_message = self.prompts(attribute=attribute)

        PROMPT_MESSAGES = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                    {"type": "text", "text": user_message},
                ],
            },
        ]
        return PROMPT_MESSAGES

    def get_tasks(
        self, image_ids: List[str], dataset: List[Dict]
    ) -> List[tuple[str, str]]:
        return super().get_tasks(image_ids, dataset)

    def prompts(self, attribute):
        return super().prompts(attribute)

    def save_model(self, data, path: Path):
        with path.open("w") as file:
            file.write(data.model_dump_json())
