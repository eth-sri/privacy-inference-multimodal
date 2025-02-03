import concurrent.futures
from abc import abstractmethod
from pathlib import Path
from typing import Dict, List

from src.configs.config import ModelConfig
from src.utils.compare import compare_label
from src.utils.parse import get_records_by_image_id
from src.utils.prompts import all_prompts
from tqdm import tqdm

from .model import BaseModel


class ApiModel(BaseModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.config = config

    @abstractmethod
    def _predict_call(self, messages: List[Dict]):
        pass

    def predict_single(self, image_id: str, attribute: str, **kwargs):
        prompt = self.apply_model_template(
            image_id=image_id, attribute=attribute, **kwargs
        )
        response = self._predict_call(messages=prompt)
        return response

    def predict_multi(self, image_ids: List[str], dataset: List[Dict], **kwargs):
        print(f"#images: {len(image_ids)}")
        tasks = self.get_tasks(image_ids=image_ids, dataset=dataset)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            future_to_image = {
                executor.submit(self.predict_single, image_id, attribute): (
                    image_id,
                    attribute,
                )
                for image_id, attribute in tasks
            }

            for future in tqdm(
                concurrent.futures.as_completed(future_to_image),
                total=len(tasks),
                desc="Processing Images",
            ):
                image, attribute = future_to_image[future]
                try:
                    data = future.result()
                    if data is not None:
                        path = Path(
                            f"{self.config.results.responses_path}/{self.config.model.name}_{self.config.prompt.type}_{self.config.results.suffix}/{image}_{attribute}.json"
                        )
                        path.parent.mkdir(parents=True, exist_ok=True)
                        self.save_model(data, path=path)
                        pass
                    else:
                        print(f"{image}: Retries exceeded.")
                except Exception as exc:
                    print(f"{image} generated an exception: {exc}")

    def apply_model_template(self, image_id: str, attribute: str, **kwargs):
        return super().apply_model_template(image_id, attribute, **kwargs)

    def get_tasks(
        self, image_ids: List[str], dataset: List[Dict]
    ) -> List[tuple[str, str]]:
        tasks = []
        for image_id in image_ids:
            existing_attributes = []
            other_attributes = []
            records = get_records_by_image_id(records=dataset, image_id=image_id)
            image_record = records[0]
            comment_record = records[-1]

            for attribute, value in image_record["label"].items():
                if (
                    "estimate" in value
                    and value["estimate"] != ""
                    and value["certainty"] >= 3
                ):
                    image_estimate = image_record["label"][attribute]["estimate"]
                    image_hardness = image_record["label"][attribute]["hardness"]
                    image_certainty = image_record["label"][attribute]["certainty"]
                    image_info_level = image_record["label"][attribute][
                        "information_level"
                    ]

                    comment_hardness = comment_record["label"][attribute]["hardness"]
                    comment_certainty = comment_record["label"][attribute]["certainty"]
                    comment_info_level = comment_record["label"][attribute][
                        "information_level"
                    ]
                    comment_estimate = comment_record["label"][attribute]["estimate"]
                    if (
                        image_hardness > 0
                        and compare_label(
                            gt_image=image_estimate,
                            gt_comments=comment_estimate,
                            attribute=attribute,
                        )
                        and image_info_level == 0
                    ):
                        existing_attributes.append(attribute)
            all_attributes = existing_attributes + other_attributes
            for attribute in all_attributes:
                tasks.append((image_id, attribute))
        return tasks

    def prompts(self, attribute):
        if self.config.prompt.single is True:
            attribute_prompt = all_prompts["attribute_specific_prompts"].get(
                attribute, attribute
            )
            if self.config.prompt.type == "complex":
                system_prompt = all_prompts["attribute_specific_prompt_single"][
                    "system"
                ]
                user_message = (
                    all_prompts["attribute_specific_prompt_single"]["header"]
                    + "\n\n"
                    + all_prompts["attribute_specific_prompts"]["free_text"]
                    + "\n"
                    + attribute_prompt
                )
            elif self.config.prompt.type == "mid":
                attribute_prompt = all_prompts["attribute_specific_prompts_mid"].get(
                    attribute, attribute
                )
                system_prompt = all_prompts["attribute_specific_prompt_single_mid"][
                    "system"
                ]
                user_message = (
                    all_prompts["attribute_specific_prompt_single_mid"]["header"]
                    + "\n\n"
                    + all_prompts["attribute_specific_prompts_mid"]["free_text"]
                    + "\n"
                    + attribute_prompt
                )
            elif self.config.prompt.type == "simple":
                attribute_prompt = all_prompts["attribute_specific_prompts_simple"].get(
                    attribute,
                    all_prompts["attribute_specific_prompts_simple"]["others"].format(
                        attribute=attribute
                    ),
                )
                system_prompt = all_prompts["attribute_specific_prompt_single_mid"][
                    "system"
                ]
                user_message = (
                    all_prompts["attribute_specific_prompt_single_mid"]["header"]
                    + "\n\n"
                    + all_prompts["attribute_specific_prompts_mid"]["free_text"]
                    + "\n"
                    + attribute_prompt
                )
        return system_prompt, user_message

    @abstractmethod
    def save_model(self, data, path: Path):
        pass
