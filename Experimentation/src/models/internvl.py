import json
from typing import Dict, List

import torch
from PIL import Image
from src.configs import ModelConfig
from src.models.hf_model import HFModel
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer, CLIPImageProcessor


class InternVL(HFModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.config = config
        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.processor = CLIPImageProcessor.from_pretrained(
            self.config.model.models_string
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model.models_string)
        self.model = (
            AutoModel.from_pretrained(
                self.config.model.models_string,
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
            )
            .eval().cuda()
        )

    def predict_multi(self, image_ids: List[str], dataset: List[Dict]):

        tasks = self.get_tasks(image_ids=image_ids, dataset=dataset)
        print("tasks", len(tasks))
        results_dict: dict = {}
        for i in tqdm(range(0, len(tasks), self.config.model.batch_size)):
            prompts = [
                dp["input"] for dp in tasks[i : i + self.config.model.batch_size]
            ]
            images = [dp["img"] for dp in tasks[i : i + self.config.model.batch_size]]
            # inputs = self.processor(
            #     prompts, images, return_tensors="pt", padding=True, truncation=True
            # ).to(self.device, torch.float16)

            # output = self.model.generate(
            #     **inputs,
            #     max_new_tokens=self.config.model.max_tokens,
            #     do_sample=False,
            #     temperature=self.config.model.temperature,
            # )
            # generated_texts = self.processor.batch_decode(
            #     output, skip_special_tokens=True
            # )

            pixel_values = self.processor(
                images=images, return_tensors="pt"
            ).pixel_values
            pixel_values = pixel_values.to(torch.bfloat16).cuda()

            generation_config = dict(
                num_beams=1,
                max_new_tokens=512,
                do_sample=False,
            )

            response = self.model.chat(
                self.tokenizer, pixel_values, prompts[0], generation_config
            )

            # Now, merge the generated results with their corresponding ID
            for dp, generated_text in zip(
                tasks[i : i + self.config.model.batch_size], [response]
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
    ) -> tuple[str, Image.Image]:

        img = Image.open(f"{self.config.data.images}/{image_id}.jpg").convert("RGB")
        img = img.resize((448, 448))
        system_prompt, user_message = self.prompts(attribute=attribute)
        prompt = user_message
        return prompt, img

    def prompts(self, attribute):
        return super().prompts(attribute)

    def get_tasks(self, image_ids: List[str], dataset: List[Dict]) -> List[Dict]:
        return super().get_tasks(image_ids, dataset)
