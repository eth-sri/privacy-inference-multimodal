import argparse

from src.configs.config import load_config
from src.utils.parse import parse_jsonl


def main():
    parser = argparse.ArgumentParser(description="config")

    parser.add_argument(
        "--config",
        type=str,
        help="Path to the config file",
        default="src/configs/config.yml",
    )

    parser.add_argument(
        "--prompt",
        type=str,
        help="prompt type",
    )

    parser.add_argument(
        "--suffix",
        type=str,
        help="suffix",
    )

    args = parser.parse_args()
    config_path = args.config
    config = load_config(config_path)
    if args.prompt:
        config.prompt.type = args.prompt
    if args.suffix:
        config.results.suffix = args.suffix

    if "cogagent" in config_path:
        from src.models.cogagent import CogAgent

        model = CogAgent(config=config)
    elif "llava1.5" in config_path:
        from src.models.llava import LLaVa

        model = LLaVa(config=config)
    elif "llava1.6" in config_path:
        from src.models.llava_next import LLaVa_Next

        model = LLaVa_Next(config=config)
    elif "idefics" in config_path:
        from src.models.idefics import Idefics

        model = Idefics(config=config)
    elif "internvl" in config_path:
        from src.models.internvl import InternVL

        model = InternVL(config=config)
    elif "openai" in config_path:
        from src.models.openai import OpenAIVLM

        model = OpenAIVLM(config=config)
    elif "gemini" in config_path:
        from src.models.google import GeminiVLMAPI

        model = GeminiVLMAPI(config=config)

    with open(config.data.dataset, "r") as file:
        labels_lines = file.read()

    all_data = parse_jsonl(jsonl_content=labels_lines)
    image_ids = []
    for idx, data in enumerate(all_data):
        image_ids.append(data["datapoint"]["image_id"])
    image_ids = list(set(image_ids))

    model.predict_multi(image_ids=image_ids, dataset=all_data)


if __name__ == "__main__":
    main()
