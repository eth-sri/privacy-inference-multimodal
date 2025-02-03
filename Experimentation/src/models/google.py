import json
import time
from typing import Dict, List

import google.generativeai as genai
from PIL import Image
from src.configs.config import ModelConfig
from src.keys import GOOGLE_API_KEY

from .api_model import ApiModel


class GeminiVLMAPI(ApiModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.config = config

        genai.configure(api_key=GOOGLE_API_KEY)

        gen_config = genai.GenerationConfig(
            temperature=self.config.model.temperature,
        )

        self.model = genai.GenerativeModel(
            self.config.model.models_string, generation_config=gen_config
        )

    def _predict_call(self, messages: List):

        retries = 0
        while retries < self.config.error_handling.max_retries:
            try:
                result = self.model.generate_content(messages, stream=False)
                return result
            except Exception as e:
                print(f"Non-rate limit error occurred: {e}")
                wait = self.config.error_handling.backoff_factor * (2**retries)
                time.sleep(wait)
                retries += 1
        return None

    def predict_single(self, image_id: str, attribute: str, **kwargs):
        return super().predict_single(image_id, attribute, **kwargs)

    def predict_multi(self, image_ids: List[str], dataset: List[Dict], **kwargs):
        return super().predict_multi(image_ids, dataset, **kwargs)

    def apply_model_template(self, image_id: str, attribute: str, **kwargs) -> List:

        image_path = f"{self.config.data.images}/{image_id}.jpg"
        img = Image.open(image_path)

        system_prompt, user_message = self.prompts(attribute=attribute)

        prompt = user_message

        return [img, prompt]

    def get_tasks(
        self, image_ids: List[str], dataset: List[Dict]
    ) -> List[tuple[str, str]]:
        return super().get_tasks(image_ids, dataset)

    def save_model(self, data, path: Image.Path):
        with path.open("w") as file:
            json.dump(type(data.candidates[0]).to_dict(data.candidates[0]), file)
