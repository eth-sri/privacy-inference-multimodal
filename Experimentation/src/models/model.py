from abc import ABC, abstractmethod
from typing import Dict, List

from src.configs import ModelConfig
from src.utils.prompts import all_prompts


class BaseModel(ABC):
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None

    @abstractmethod
    def predict_multi(self, image_ids: List[str], dataset: List[Dict], **kwargs):
        pass

    @abstractmethod
    def apply_model_template(self, image_id: str, attribute: str, **kwargs):
        pass

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
            elif self.config.prompt.type == "simplest":
                attribute_prompt = all_prompts["attribute_specific_prompts_simple"].get(
                    attribute,
                    all_prompts["attribute_specific_prompts_simple"]["others"].format(
                        attribute=attribute
                    ),
                )
                system_prompt = all_prompts["attribute_specific_prompts_simple"][
                    "system"
                ]
                user_message = (
                    all_prompts["attribute_specific_prompts_simple"]["header"]
                    + "\n\n"
                    + all_prompts["attribute_specific_prompts_simple"]["free_text"]
                    + "\n"
                    + attribute_prompt
                )
            elif self.config.prompt.type == "oss":
                attribute_prompt = all_prompts["individual_simple_prompts"].get(
                    attribute,
                    all_prompts["individual_simple_prompts"]["others"].format(
                        others=attribute
                    ),
                )
                system_prompt = all_prompts["attribute_specific_prompt_single_mid"][
                    "system"
                ]
                user_message = attribute_prompt
            return system_prompt, user_message
        else:
            raise NotImplementedError
