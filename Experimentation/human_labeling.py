import argparse
import json
import os
from pathlib import Path

from src.configs.config import load_config
from src.utils.compare import compare_label
from src.utils.dataset import filter_dataset
from src.utils.parse import (
    format_model_answer_with_inference,
    get_records_by_image_id,
    guess_key_map,
    parse_jsonl,
    parse_jsonl_unique,
)


def main():  # noqa: C901

    parser = argparse.ArgumentParser(description="Label-Prediction comparison by human")

    parser.add_argument(
        "--config",
        type=str,
        help="Path to the config file",
        default="../../configs/config.yaml",
    )

    parser.add_argument(
        "--attribute",
        type=str,
        help="Specific attribute human wants to compare",
        default="location",
    )

    parser.add_argument(
        "--gt",
        type=str,
        help="Which ground truth to look for",
        default="image",
        choices=["comment", "image"],
    )

    parser.add_argument(
        "--true_pred",
        type=int,
        help="Give all the wrong or right predictions",
        default=2,
        choices=[-1, 0, 1, 2, 3, 4, 5, 6],
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
    save_folder = f"{config.results.responses_path}/{config.model.name}_{config.prompt.type}_{config.results.suffix}"
    predictions_folder = Path(save_folder)
    gt_source = args.gt
    attribute = args.attribute
    model_name = config.model.name
    performance_path = Path(
        f"{args.performance}/{gt_source}_performance_{model_name}_{config.prompt.type}_{config.results.suffix}.json"
    )
    true_pred = args.true_pred

    # performance_path = "performances/image_performance_cogagent_single.json"
    # predictions_folder = ""

    ids = []
    not_exist = []
    num_checked = 0

    try:
        with open(labels_path, "r") as file:
            labels_lines = file.read()
    except FileNotFoundError:
        raise AssertionError("Labels file doesn't exist.")

    try:
        with open(performance_path, "r") as file:
            performance = json.load(file)
    except FileNotFoundError:
        raise AssertionError("Performance file doesn't exist.")

    results = None
    try:
        with open(
            f"{config.results.results_path}_{config.model.name}_{config.prompt.type}_{config.results.suffix}.json",
            "r",
        ) as file:
            results = json.load(file)
    except Exception:
        print("not os model")

    parsed_data = parse_jsonl_unique(jsonl_content=labels_lines)
    all_data = parse_jsonl(jsonl_content=labels_lines)

    for idx, image in enumerate(parsed_data):
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
        model_attribute_answer = ""

        for key, value in performance[image_id].items():
            image_estimate = image_label["label"][attribute]["estimate"]
            image_hardness = image_label["label"][attribute]["hardness"]
            image_certainty = image_label["label"][attribute]["certainty"]
            image_info_level = image_label["label"][attribute]["information_level"]

            comment_hardness = comment_label["label"][attribute]["hardness"]
            comment_certainty = comment_label["label"][attribute]["certainty"]
            comment_info_level = comment_label["label"][attribute]["information_level"]
            comment_estimate = comment_label["label"][attribute]["estimate"]
            if (
                image_hardness > 0
                and compare_label(
                    gt_image=image_estimate,
                    gt_comments=comment_estimate,
                    attribute=key,
                )
                and image_info_level == 0
            ):
                if key == attribute:
                    model_attribute_answer = ""
                    file = f"{image_id}_{key}.json"
                    file_path = os.path.join(predictions_folder, file)
                    try:
                        if os.path.getsize(file_path) > 0:
                            with open(file_path, "r") as f:
                                model_response = json.load(f)
                                if dict_key_check in model_response:
                                    if "gemini" in model_name:
                                        # model_answer = model_answer + '\n\n' + model_response['content']['parts'][0]['text']
                                        # if file.split('_')[1] == f'{attribute}.json':
                                        model_attribute_answer = model_response[
                                            "content"
                                        ]["parts"][0]["text"]
                                    else:
                                        # model_answer = model_answer + '\n\n' + model_response['choices'][0]['message']['content']
                                        # if file.split('_')[1] == f'{attribute}.json':
                                        model_attribute_answer = model_response[
                                            "choices"
                                        ][0]["message"]["content"]
                    except json.JSONDecodeError:
                        not_exist.append(file)
                        print(f"Error decoding JSON from {file_path}")
                    except Exception:
                        print(f"file {file_path} doesnot exist")

                        # model_answer = model_response['choices'][0]['message']['content']
                    formatted_model_answer = format_model_answer_with_inference(
                        model_answer=model_attribute_answer
                    )

                    for pred_key, guesses in formatted_model_answer.items():
                        if performance[image_id][key]["true_pred"] == true_pred:
                            if (
                                config.prompt.single
                                or guess_key_map(pred_key) == key
                                or (
                                    guess_key_map(pred_key) == "location"
                                    and key == "placeOfImage"
                                )
                            ):
                                num_checked += 1
                                print("".join(["#"] * 200))
                                print(f"Model answer: {model_attribute_answer}\n")
                                print("".join(["-"] * 200))
                                if results:
                                    print(f"Model output: {results[image_id][key]}\n")
                                for pred_key, guesses in formatted_model_answer.items():
                                    right_guess = None
                                    if guess_key_map(pred_key) == key or (
                                        guess_key_map(pred_key) == "location"
                                        and key == "placeOfImage"
                                    ):
                                        right_guess = guesses["guess"][0]
                                        break
                                print(
                                    f"{right_guess} | {data['label'][key]['estimate']} | {image_id}",
                                    flush=True,
                                )

                                # Request user input
                                human_label = input(": ")

                                if human_label == "inf":
                                    print(guesses["inference"])
                                    human_label = input(": ")
                                if human_label == "mod":
                                    print(model_answer)
                                    human_label = input(": ")
                                if human_label == "q" or human_label == "":
                                    break

                                performance[image_id][key]["true_pred"] = int(
                                    human_label
                                )
                                if int(human_label) >= 0:
                                    performance[image_id][key]["total_pred"] = 1

                                ids.append(image_id)

                            elif guess_key_map(pred_key) == (key, False):
                                num_checked += 1
                                print(
                                    f"{guesses['guess']} | {data['label']['others'][key]['estimate']} | {image_id}",
                                    flush=True,
                                )
                                ids.append(image_id)
                            break
                    if len(formatted_model_answer) == 0:
                        if key == attribute:
                            if performance[image_id][key]["true_pred"] == true_pred:
                                num_checked += 1
                                print(
                                    f"Model answer: {model_attribute_answer} | {data['label'][key]['estimate']} | {image_id}"
                                )
                                # Request user input
                                human_label = input(": ")

                                if human_label == "inf":
                                    print(guesses["inference"])
                                    human_label = input(": ")
                                if human_label == "mod":
                                    print(model_answer)
                                    human_label = input(": ")
                                if human_label == "q" or human_label == "":
                                    break

                                performance[image_id][key]["true_pred"] = int(
                                    human_label
                                )
                                if int(human_label) >= 0:
                                    performance[image_id][key]["total_pred"] = 1

                                ids.append(image_id)

    print("num checked", num_checked)
    print(len(ids), ids)
    print("not exist")
    print(not_exist)
    print("not exist length", len(not_exist))

    with open(performance_path, "w") as file:
        json.dump(performance, file)


if __name__ == "__main__":
    main()
