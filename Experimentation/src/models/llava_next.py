import json
from typing import Dict, List

import torch
from llava.eval.run_llava import eval_model
from llava.mm_utils import get_model_name_from_path
from llava.model.builder import load_pretrained_model
from PIL import Image
from src.configs import ModelConfig
from src.models.hf_model import HFModel
from tqdm import tqdm


class LLaVa_Next(HFModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.config = config
        self.device = 0 if torch.cuda.is_available() else "cpu"

        self.tokenizer, self.model, self.image_processor, self.context_len = (
            load_pretrained_model(
                model_path=self.config.model.models_string,
                model_base=None,
                model_name=get_model_name_from_path(self.config.model.models_string),
                # load_4bit=True
            )
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
            image_paths = [dp["image_id"] for dp in tasks[i : i + self.config.model.batch_size]]



            args = type('Args', (), {
                "model_path": self.config.model.models_string,
                "model_base": None,
                "model_name": get_model_name_from_path(self.config.model.models_string),
                "query": prompts[0],
                "conv_mode": None,
                "image_file": f"images/{image_paths[0]}.jpg",
                "sep": ",",
                "temperature": 0,
                "top_p": None,
                "num_beams": 1,
                "max_new_tokens": 512
            })()

            outputs = eval_model(args, model_name=self.config.model.models_string, tokenizer=self.tokenizer, model=self.model, image_processor=self.image_processor, context_len=self.context_len)


            # inputs = self.tokenizer(
            #     prompts, return_tensors="pt", padding=True, truncation=True
            # ).to(self.device, torch.float16)
            # images = self.image_processor(images, return_tensors="pt")

            # output = self.model.generate(
            #     **inputs,
            #     **images,
            #     max_new_tokens=self.config.model.max_tokens,
            #     do_sample=False,
            #     temperature=self.config.model.temperature,
            # )
            # generated_texts = self.processor.batch_decode(
            #     output, skip_special_tokens=True
            # )
            # print(processor.decode(output[0][2:], skip_special_tokens=True))

            # Now, merge the generated results with their corresponding ID
            for dp, generated_text in zip(
                tasks[i : i + self.config.model.batch_size], [outputs]
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

        img = Image.open(f"{self.config.data.images}/{image_id}.jpg")
        system_prompt, user_message = self.prompts(attribute=attribute)
        prompt = user_message
        return prompt, img

    def prompts(self, attribute):
        return super().prompts(attribute)

    def get_tasks(self, image_ids: List[str], dataset: List[Dict]) -> List[Dict]:
        return super().get_tasks(image_ids, dataset)
