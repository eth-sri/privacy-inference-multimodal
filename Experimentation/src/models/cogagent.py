import json
from typing import Dict, List

import torch
from PIL import Image
from src.configs import ModelConfig
from src.models.hf_model import HFModel
from tqdm import tqdm
from transformers import AutoModelForCausalLM, LlamaTokenizer


class CogAgent(HFModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.config = config

        MODEL_PATH = self.config.model.models_string
        TOKENIZER_PATH = "lmsys/vicuna-7b-v1.5"
        self.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        bf16 = True

        self.tokenizer = LlamaTokenizer.from_pretrained(TOKENIZER_PATH)
        if bf16:
            self.torch_type = torch.bfloat16
        else:
            self.torch_type = torch.float16

        print(
            "========Use torch type as:{} with device:{}========\n\n".format(
                self.torch_type, self.DEVICE
            )
        )

        self.model = (
            AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                torch_dtype=self.torch_type,
                low_cpu_mem_usage=True,
                load_in_4bit=False,
                trust_remote_code=True,
            )
            .to(self.DEVICE)
            .eval()
        )

    def predict_multi(self, image_ids: List[str], dataset: List[Dict]):

        tasks = self.get_tasks(image_ids=image_ids, dataset=dataset)
        print("tasks", len(tasks))
        results_dict: dict = {}
        for i in tqdm(range(0, len(tasks), self.config.model.batch_size)):
            history = []
            query = [dp["input"] for dp in tasks[i : i + self.config.model.batch_size]]
            images = [dp["img"] for dp in tasks[i : i + self.config.model.batch_size]]
            input_by_model = self.model.build_conversation_input_ids(
                self.tokenizer, query=query[0], history=history, images=images
            )
            inputs = {
                "input_ids": input_by_model["input_ids"].unsqueeze(0).to(self.DEVICE),
                "token_type_ids": input_by_model["token_type_ids"]
                .unsqueeze(0)
                .to(self.DEVICE),
                "attention_mask": input_by_model["attention_mask"]
                .unsqueeze(0)
                .to(self.DEVICE),
                "images": [
                    [input_by_model["images"][0].to(self.DEVICE).to(self.torch_type)]
                ],
            }
            if "cross_images" in input_by_model and input_by_model["cross_images"]:
                inputs["cross_images"] = [
                    [
                        input_by_model["cross_images"][0]
                        .to(self.DEVICE)
                        .to(self.torch_type)
                    ]
                ]

            # add any transformers params here.
            gen_kwargs = {
                "max_length": self.config.model.max_tokens,
                "temperature": self.config.model.temperature,
                "do_sample": False,
            }
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **gen_kwargs)
                # print('outputs1', outputs)
                outputs = outputs[:, inputs["input_ids"].shape[1] :]
                # print('outputs2', outputs)
                response = self.tokenizer.decode(outputs[0])
                # print('response1', response)
                response = response.split("</s>")[0]
                print("\nCog:", response)
            # history.append((query, response))
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
        system_prompt, user_message = self.prompts(attribute=attribute)
        prompt = user_message
        return prompt, img

    def get_tasks(self, image_ids: List[str], dataset: List[Dict]) -> List[Dict]:
        return super().get_tasks(image_ids, dataset)

    def prompts(self, attribute):
        return super().prompts(attribute)
