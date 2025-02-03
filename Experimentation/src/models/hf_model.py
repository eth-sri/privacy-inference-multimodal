from typing import Dict, List

from src.configs import ModelConfig
from src.utils.compare import compare_label
from src.utils.parse import get_records_by_image_id
from tqdm import tqdm

from .model import BaseModel


class HFModel(BaseModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)

    def get_tasks(self, image_ids: List[str], dataset: List[Dict]) -> List[dict]:
        # create tasks here a list of (image_path,attribute)
        tasks = []
        for image_id in tqdm(image_ids):
            records = get_records_by_image_id(dataset, image_id)
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
                        prompt, img = self.apply_model_template(
                            image_id=image_id, attribute=attribute
                        )
                        dp = {
                            "image_id": image_id,
                            "attribute": attribute,
                            "input": prompt,
                            "img": img,
                        }
                        tasks.append(dp)
                elif attribute == "others":
                    for other_attribute in value.keys():
                        prompt, img = self.apply_model_template(
                            image_id=image_id, attribute=other_attribute
                        )
                        dp = {
                            "image_id": image_id,
                            "attribute": other_attribute,
                            "input": prompt,
                            "img": img,
                        }
                        tasks.append(dp)
        print(prompt)
        return tasks

    def prompts(self, attribute):
        return super().prompts(attribute)
