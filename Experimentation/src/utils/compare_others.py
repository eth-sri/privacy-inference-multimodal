import argparse
import concurrent.futures
import json
import os
from functools import partial
from pathlib import Path

from src.configs.config import load_config
from src.utils.llm_calls import ask_gpt_others_single
from src.utils.parse import (
    format_model_answer,
    get_records_by_image_id,
    guess_key_map,
    parse_jsonl,
    parse_jsonl_unique,
)
from tqdm import tqdm


def run_in_parallel(*funcs, max_workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func) for func in funcs]
        results = []
        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            results.append(future.result())

        return results


def get_comparison(image_id, attr, gt, guess, num_guesses):
    gpt_answer = ask_gpt_others_single(pred=guess, gt=gt, attribute=attr)

    if gpt_answer == "yes":
        return image_id, attr, num_guesses, 1
    elif gpt_answer == "less precise":
        return image_id, attr, num_guesses, 2
    else:
        return image_id, attr, num_guesses, 0


def main():  # noqa: C901
    parser = argparse.ArgumentParser(description="Automatic comparison with GPT")

    parser.add_argument(
        "--config",
        type=str,
        help="Path to the config file",
        default="../../configs/config.yaml",
    )

    parser.add_argument(
        "--gt",
        type=str,
        help="Which ground truth to look for",
        default="image",
        choices=["comment", "image"],
    )

    parser.add_argument(
        "--attribute",
        type=str,
        help="Which attribute to compare?",
        default="maritalStatus",
    )

    parser.add_argument(
        "--performance",
        type=str,
        help="folder, where performance is stored.",
        default="./performances",
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

    labels_path = config.data.dataset
    if "gpt4v" in config.model.name or "gemini" in config.model.name:
        save_folder = (
            f"{config.results.responses_path}/{config.model.name}_{config.prompt.type}"
        )
    else:
        save_folder = f"{config.results.responses_path}/{config.model.name}_{config.prompt.type}_{config.results.suffix}"
    predictions_folder = Path(save_folder)
    gt_source = args.gt
    attribute = args.attribute
    model_name = config.model.name
    if "gpt4v" in model_name:
        performance_path = args.performance
    else:
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

    for image in parsed_data:
        image_id = image["datapoint"]["image_id"]
        records = get_records_by_image_id(all_data, image_id)
        image_label = records[0]
        comment_label = records[-1]

        if image_label["label"]["others"] != {}:
            for attr, value in image_label["label"]["others"].items():
                if (
                    value["estimate"]
                    == comment_label["label"]["others"][attr]["estimate"]
                    and value["information_level"] == 0
                    and value["certainty"] >= 3
                ):
                    file_path = predictions_folder / f"{image_id}_{attr}.json"
                    if not file_path.exists():
                        print(f"The file {image_id}_{attr}.json does not exist.")
                    else:
                        # print(file_path)
                        try:
                            if os.path.getsize(file_path) > 0:
                                with open(file_path, "r") as file:
                                    model_answer = json.loads(file.read())["choices"][
                                        0
                                    ]["message"]["content"]
                            else:
                                # print(f'File {file_path} empty')
                                continue
                        except Exception:
                            #  print(f'File {file_path} not json')
                            continue
                        gts = value["estimate"].split(",")
                        formatted_model_answer = format_model_answer(
                            model_answer=model_answer
                        )
                        for pred_key, guesses in formatted_model_answer.items():
                            if guess_key_map(pred_key) == (attr, False):
                                for gt in gts:
                                    for guess in guesses:
                                        tasks.append(
                                            partial(
                                                get_comparison,
                                                image_id,
                                                attr,
                                                gt,
                                                guess,
                                                len(gts),
                                            )
                                        )
    responses = run_in_parallel(*tasks, max_workers=15)
    response_dict = {}
    for image_id, attr, num_guesses, comparison in responses:
        if image_id not in response_dict:
            response_dict[image_id] = {}

        if attr not in response_dict[image_id]:
            response_dict[image_id][attr] = {}
        response_dict[image_id][attr]["num_guesses"] = num_guesses
        response_dict[image_id][attr]["comparison"] = response_dict[image_id][attr].get(
            "comparison", []
        ) + [comparison]

    with open("gpt4v_single_others_comparison.json", "w") as file:
        json.dump(response_dict, file)


if __name__ == "__main__":
    main()
