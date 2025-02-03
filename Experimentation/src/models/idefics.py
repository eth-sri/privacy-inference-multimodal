import json
from typing import Dict, List

import torch
from PIL import Image
from src.configs import ModelConfig
from src.models.hf_model import HFModel
from tqdm import tqdm
from transformers import AutoProcessor, BitsAndBytesConfig, IdeficsForVisionText2Text


class Idefics(HFModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.config = config

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        quantization = BitsAndBytesConfig(load_in_4bit=True)

        checkpoint = self.config.model.models_string
        self.processor = AutoProcessor.from_pretrained(
            checkpoint, torch_dtype=torch.bfloat16
        )
        self.model = IdeficsForVisionText2Text.from_pretrained(
            checkpoint, torch_dtype=torch.bfloat16, quantization_config=quantization
        )

        # Generation args
        self.exit_condition = self.processor.tokenizer(
            "<end_of_utterance>", add_special_tokens=False
        ).input_ids
        self.bad_words_ids = self.processor.tokenizer(
            ["<image>", "<fake_token_around_image>"], add_special_tokens=False
        ).input_ids

    def predict_multi(self, image_ids: List[str], dataset: List[Dict]):

        tasks = self.get_tasks(image_ids=image_ids, dataset=dataset)
        print("tasks", len(tasks))
        results_dict: dict = {}
        for i in tqdm(range(0, len(tasks), self.config.model.batch_size)):
            prompts = [
                dp["input"] for dp in tasks[i : i + self.config.model.batch_size]
            ]
            inputs = self.processor(
                prompts, add_end_of_utterance_token=False, return_tensors="pt"
            ).to(self.device)
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    eos_token_id=self.exit_condition,
                    bad_words_ids=self.bad_words_ids,
                    max_length=500,
                    temperature=self.config.model.temperature,
                )
            generated_texts = self.processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )
            for dp, generated_text in zip(
                tasks[i : i + self.config.model.batch_size], generated_texts
            ):
                if dp["image_id"] not in results_dict:
                    results_dict[dp["image_id"]] = {}
                results_dict[dp["image_id"]][dp["attribute"]] = generated_text

        with open(
            f"{self.config.results.results_path}_{self.config.model.name}_{self.config.prompt.type}_{self.config.results.suffix}.json",
            "w",
        ) as file:
            json.dump(results_dict, file)

    def apply_model_template(
        self, image_id: str, attribute: str, **kwargs
    ) -> tuple[list, Image.Image]:

        img = Image.open(f"{self.config.data.images}/{image_id}.jpg")
        system_prompt, user_message = self.prompts(attribute=attribute)
        prompt = [
            img,
            f"User: {user_message}",
            "<end_of_utterance>",
            "\nAssistant: ",
        ]
        return prompt, img

    def prompts(self, attribute):
        return super().prompts(attribute)

    def get_tasks(self, image_ids: List[str], dataset: List[Dict]) -> List[Dict]:
        return super().get_tasks(image_ids, dataset)
