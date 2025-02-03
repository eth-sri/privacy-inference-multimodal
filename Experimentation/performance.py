import argparse
import json
from pathlib import Path

import pandas as pd
from src.configs.config import load_config
from src.utils.dataset import filter_dataset
from src.utils.parse import get_records_by_image_id, parse_jsonl, parse_jsonl_unique


def get_performance_summary(  # noqa: C901
    # config_path: str = "../../configs/config.yaml",
    config,
    gt_source: str = "image",
    performance=None,
):

    # config_path = args.config
    # config = load_config(config_path)

    labels_path = config.data.dataset
    # gt_source = args.gt
    # attribute = args.attribute
    model_name = config.model.name
    # Check if --performance was provided, if not set a default value
    if performance is None:
        performance = "./performances"
        performance_path = Path(
            f"{performance}/{gt_source}_performance_{model_name}_{config.prompt.type}_{config.results.suffix}.json"
        )
    else:
        performance_path = performance

    try:
        with open(labels_path, "r") as file:
            labels_lines = file.read()
    except FileNotFoundError:
        raise AssertionError("Labels file doesn't exist.")

    with open(performance_path, "r") as file:
        performance = json.load(file)

    parsed_data = parse_jsonl_unique(jsonl_content=labels_lines)
    all_data = parse_jsonl(jsonl_content=labels_lines)

    ids = []

    performance_summary = {}
    for image in parsed_data:
        image_id = image["datapoint"]["image_id"]
        records = get_records_by_image_id(all_data, image_id)
        image_label = records[0]
        comment_label = records[-1]

        if gt_source == "image":
            data = image_label
        elif gt_source == "comment":
            data = comment_label

        for attribute_key, label in data["label"].items():
            # Conditions
            records = get_records_by_image_id(all_data, image_id)
            image_record = records[0]
            comment_record = records[-1]
            if filter_dataset(image_label, comment_label, attribute_key, label):
                if attribute_key not in performance_summary:
                    performance_summary[attribute_key] = {}
                if image_id in performance:
                    performance_summary[attribute_key]["total_gt"] = (
                        performance_summary[attribute_key].get("total_gt", 0)
                        + performance[image_id][attribute_key]["total_gt"]
                    )
                    if "total_pred" in performance[image_id][attribute_key]:
                        performance_summary[attribute_key]["total_pred"] = (
                            performance_summary[attribute_key].get("total_pred", 0)
                            + performance[image_id][attribute_key]["total_pred"]
                        )
                    else:
                        # print(image_id, attribute_key)
                        ids.append(image_id)
                    if performance[image_id][attribute_key]["true_pred"] >= 1:
                        performance_summary[attribute_key]["true_pred"] = (
                            performance_summary[attribute_key].get("true_pred", 0) + 1
                        )

    # print(performance_summary)

    # Transforming the data into a format suitable for DataFrame creation
    df_data = {"Category": [], "total_gt": [], "total_pred": [], "true_pred": []}

    for key, value in performance_summary.items():
        df_data["Category"].append(key)
        df_data["total_gt"].append(value.get("total_gt", 0))
        df_data["total_pred"].append(value.get("total_pred", 0))
        df_data["true_pred"].append(value.get("true_pred", 0))

    # Creating the DataFrame
    df = pd.DataFrame(df_data)
    # print(df.to_string(index=False))
    return df[df["Category"] != "placeOfBirth"]


def get_performance_summary_human(  # noqa: C901
    # config_path: str = "../../configs/config.yaml",
    config,
    gt_source: str = "image",
    performance=None,
):

    # config_path = args.config
    # config = load_config(config_path)

    labels_path = config.data.dataset
    # gt_source = args.gt
    # attribute = args.attribute
    model_name = config.model.name
    # Check if --performance was provided, if not set a default value
    if performance is None:
        performance = "./performances"
        performance_path = Path(
            f"{performance}/{gt_source}_performance_{model_name}_{config.prompt.type}_{config.results.suffix}.json"
        )
    else:
        performance_path = performance

    try:
        with open(labels_path, "r") as file:
            labels_lines = file.read()
    except FileNotFoundError:
        raise AssertionError("Labels file doesn't exist.")

    with open(performance_path, "r") as file:
        performance = json.load(file)

    df = pd.read_csv("dataset/datapoints.csv")

    parsed_data = parse_jsonl_unique(jsonl_content=labels_lines)
    all_data = parse_jsonl(jsonl_content=labels_lines)

    ids = []

    performance_summary1 = {}
    for image in parsed_data:
        image_id = image["datapoint"]["image_id"]
        records = get_records_by_image_id(all_data, image_id)
        image_label = records[0]
        comment_label = records[-1]

        if gt_source == "image":
            data = image_label
        elif gt_source == "comment":
            data = comment_label

        for attribute_key, label in data["label"].items():
            # Conditions
            records = get_records_by_image_id(all_data, image_id)
            image_record = records[0]
            comment_record = records[-1]
            human = df.loc[
                (df["image_id"] == image_id) & (df["attribute"] == attribute_key)
            ]["humans"].values
            if (
                filter_dataset(image_label, comment_label, attribute_key, label)
                and not human
            ):
                if attribute_key not in performance_summary1:
                    performance_summary1[attribute_key] = {}
                if image_id in performance:
                    performance_summary1[attribute_key]["total_gt"] = (
                        performance_summary1[attribute_key].get("total_gt", 0)
                        + performance[image_id][attribute_key]["total_gt"]
                    )
                    if "total_pred" in performance[image_id][attribute_key]:
                        performance_summary1[attribute_key]["total_pred"] = (
                            performance_summary1[attribute_key].get("total_pred", 0)
                            + performance[image_id][attribute_key]["total_pred"]
                        )
                    else:
                        # print(image_id, attribute_key)
                        ids.append(image_id)
                    if performance[image_id][attribute_key]["true_pred"] >= 1:
                        performance_summary1[attribute_key]["true_pred"] = (
                            performance_summary1[attribute_key].get("true_pred", 0) + 1
                        )
    performance_summary2 = {}
    for image in parsed_data:
        image_id = image["datapoint"]["image_id"]
        records = get_records_by_image_id(all_data, image_id)
        image_label = records[0]
        comment_label = records[-1]

        if gt_source == "image":
            data = image_label
        elif gt_source == "comment":
            data = comment_label

        for attribute_key, label in data["label"].items():
            # Conditions
            records = get_records_by_image_id(all_data, image_id)
            image_record = records[0]
            comment_record = records[-1]
            human = df.loc[
                (df["image_id"] == image_id) & (df["attribute"] == attribute_key)
            ]["humans"].values
            if (
                filter_dataset(image_label, comment_label, attribute_key, label)
                and human
            ):
                if attribute_key not in performance_summary2:
                    performance_summary2[attribute_key] = {}
                if image_id in performance:
                    performance_summary2[attribute_key]["total_gt"] = (
                        performance_summary2[attribute_key].get("total_gt", 0)
                        + performance[image_id][attribute_key]["total_gt"]
                    )
                    if "total_pred" in performance[image_id][attribute_key]:
                        performance_summary2[attribute_key]["total_pred"] = (
                            performance_summary2[attribute_key].get("total_pred", 0)
                            + performance[image_id][attribute_key]["total_pred"]
                        )
                    else:
                        # print(image_id, attribute_key)
                        ids.append(image_id)
                    if performance[image_id][attribute_key]["true_pred"] >= 1:
                        performance_summary2[attribute_key]["true_pred"] = (
                            performance_summary2[attribute_key].get("true_pred", 0) + 1
                        )

    # Transforming the data into a format suitable for DataFrame creation
    df_data1 = {"Category": [], "total_gt": [], "total_pred": [], "true_pred": []}

    for key, value in performance_summary1.items():
        df_data1["Category"].append(key)
        df_data1["total_gt"].append(value.get("total_gt", 0))
        df_data1["total_pred"].append(value.get("total_pred", 0))
        df_data1["true_pred"].append(value.get("true_pred", 0))

        # Transforming the data into a format suitable for DataFrame creation
    df_data2 = {"Category": [], "total_gt": [], "total_pred": [], "true_pred": []}

    for key, value in performance_summary2.items():
        df_data2["Category"].append(key)
        df_data2["total_gt"].append(value.get("total_gt", 0))
        df_data2["total_pred"].append(value.get("total_pred", 0))
        df_data2["true_pred"].append(value.get("true_pred", 0))

    # Creating the DataFrame
    df1 = pd.DataFrame(df_data1)
    df2 = pd.DataFrame(df_data2)
    df1 = df1[df1["Category"] != "placeOfBirth"]
    df2 = df2[df2["Category"] != "placeOfBirth"]

    print(df1["true_pred"].sum() / df1["total_gt"].sum())

    print(df2["true_pred"].sum() / df2["total_gt"].sum())

    # print(df.to_string(index=False))
    return (
        df1[df1["Category"] != "placeOfBirth"],
        df2[df2["Category"] != "placeOfBirth"],
    )


if __name__ == "__main__":
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
        # default="./performances",
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

    df = get_performance_summary(config=config, performance=args.performance)
    print(df["true_pred"].sum() / df["total_gt"].sum())
    print(df.to_string(index=False))
