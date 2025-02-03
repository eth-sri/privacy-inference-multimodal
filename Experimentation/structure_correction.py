import argparse
import concurrent.futures
import json
from pathlib import Path

from src.configs.config import load_config
from src.utils.dataset import filter_dataset
from src.utils.llm_calls import correct_structure, correct_structure_simple
from src.utils.parse import get_records_by_image_id, parse_jsonl, parse_jsonl_unique
from tqdm import tqdm


def correct_parallel(function, save_folder: str, tasks=[]):

    # print(f'#images: {len(image_paths)}')
    max_workers = 15

    print(f"#tasks {len(tasks)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_image = {
            executor.submit(function, text, image_id, attribute): (
                image_id,
                attribute,
            )
            for text, image_id, attribute in tasks
        }

        for future in tqdm(
            concurrent.futures.as_completed(future_to_image),
            total=len(tasks),
            desc="Processing Images",
        ):
            image_id, attribute = future_to_image[future]
            try:
                data = future.result()
                if data is not None:
                    path = Path(f"{save_folder}/{image_id}_{attribute}.json")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("w") as file:
                        file.write(data.model_dump_json())

                else:
                    print(f"{image_id} {attribute}: Retries exceeded.")
            except Exception as exc:
                print(f"{image_id} {attribute} generated an exception: {exc}")


def main():  # noqa: C901
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

    parser.add_argument(
        "--base_folder",
        type=str,
        help="vlm output folder",
        default="model_responses/gpt4v_single",
    )

    parser.add_argument(
        "--gt",
        type=str,
        help="ground truth source whether from comments or images",
        default="image",
    )

    parser.add_argument(
        "--performance",
        type=str,
        help="folder, where performance is stored.",
        default="./performances",
    )

    args = parser.parse_args()
    config_path = args.config
    config = load_config(config_path)
    if args.prompt:
        config.prompt.type = args.prompt
    if args.suffix:
        config.results.suffix = args.suffix

    with open(
        f"{config.results.results_path}_{config.model.name}_{config.prompt.type}_{config.results.suffix}.json",
        "r",
    ) as file:
        results = json.load(file)

    tasks = []

    if config.prompt.type == "simple":
        correct_str = correct_structure_simple
    else:
        correct_str = correct_structure

    print(correct_str)

    if "gpt4v" not in config.model.name and "gemini" not in config.model.name:

        with open(
            f"{config.results.results_path}_{config.model.name}_{config.prompt.type}_{config.results.suffix}.json",
            "r",
        ) as file:
            results = json.load(file)

        separator = ""
        if "llava1.5" in config.model.name:
            separator = "\nASSISTANT:"
        elif "idefics" in config.model.name:
            separator = "\nAssistant:"

        for img_id, response in results.items():
            for attr, text in response.items():
                if separator != "":
                    index = text.find(separator)
                    start_index = index + len(separator + " ")
                    text = text[start_index:]
                tasks.append((text, img_id, attr))

    else:
        labels_path = config.data.dataset
        save_folder = f"{config.results.responses_path}/{config.model.name}_{config.prompt.type}_{config.results.suffix}"
        predictions_folder = Path(args.base_folder)
        gt_source = args.gt
        attribute = args.attribute
        model_name = config.model.name
        performance_path = Path(
            f"{args.performance}/{gt_source}_performance_{model_name}_{config.prompt.type}_{config.results.suffix}.json"
        )

        try:
            with open(labels_path, "r") as file:
                labels_lines = file.read()
        except FileNotFoundError:
            raise AssertionError("Labels file doesn't exist.")

        parsed_data = parse_jsonl_unique(jsonl_content=labels_lines)
        all_data = parse_jsonl(jsonl_content=labels_lines)

        performance = {}

        if performance_path.is_file():
            with open(performance_path, "r") as file:
                performance = json.load(file)

        tasks = []

        idx = 0

        for image in parsed_data:
            image_id = image["datapoint"]["image_id"]
            records = get_records_by_image_id(all_data, image_id)
            image_label = records[0]
            comment_label = records[-1]

            if gt_source == "image":
                data = image_label
            elif gt_source == "comment":
                data = comment_label

            dict_key_check = "content" if "gemini" in model_name else "choices"

            model_answer = ""

            if image_id not in performance:
                performance[image_id] = {}

            for attribute_key, label in data["label"].items():
                if filter_dataset(image_label, comment_label, attribute_key, label):
                    if attribute_key not in performance[image_id]:
                        performance[image_id][attribute_key] = {}
                    # performance[image_id][attribute_key] = performance.get(attribute_key, {})
                    gt = label["estimate"]
                    performance[image_id][attribute_key]["total_gt"] = 1
                    performance[image_id][attribute_key]["idx"] = idx
                    try:
                        file_path = (
                            predictions_folder / f"{image_id}_{attribute_key}.json"
                        )
                        with open(file_path, "r") as f:
                            model_response = json.load(f)
                            if dict_key_check in model_response:
                                if "gemini" in model_name:
                                    model_answer = model_response["content"]["parts"][
                                        0
                                    ]["text"]
                                else:
                                    model_answer = model_response["choices"][0][
                                        "message"
                                    ]["content"]
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from {file_path}")
                        # continue
                    except Exception as e:
                        print(f"Error {e}")
                        # continue
                    tasks.append((model_answer, image_id, attribute_key))

    correct_parallel(
        function=correct_str,
        save_folder=f"{config.results.responses_path}/{config.model.name}_{config.prompt.type}_{config.results.suffix}",
        tasks=tasks,
    )


if __name__ == "__main__":

    main()
