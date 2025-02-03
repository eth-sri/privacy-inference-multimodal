import argparse
import json


def filter_dataset(image_record, comment_record, attribute, dp):

    from src.utils.compare import compare_label

    if "estimate" in dp and dp["estimate"] != "" and dp["certainty"] >= 3:
        image_estimate = image_record["label"][attribute]["estimate"]
        image_hardness = image_record["label"][attribute]["hardness"]
        image_certainty = image_record["label"][attribute]["certainty"]
        image_info_level = image_record["label"][attribute]["information_level"]

        comment_hardness = comment_record["label"][attribute]["hardness"]
        comment_certainty = comment_record["label"][attribute]["certainty"]
        comment_info_level = comment_record["label"][attribute]["information_level"]
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
            return True
        else:
            return False


def generate_df(path: str):
    import pandas as pd
    from src.utils.parse import get_records_by_image_id, parse_jsonl, parse_jsonl_unique

    with open(f"{path}humans.jsonl", "r") as file:
        jsonl_content = file.read()
        humans = {}
        lines = jsonl_content.strip().split("\n")
        for line in lines:
            record = json.loads(line)
            image_id = list(record.keys())[0]
            humans[image_id] = list(record.values())[0]

    with open(f"{path}dataset.jsonl", "r") as file:
        json_lines = file.read()
    parsed_data = parse_jsonl_unique(jsonl_content=json_lines)
    all_data = parse_jsonl(jsonl_content=json_lines)

    rows = []

    for image in parsed_data:
        image_id = image["datapoint"]["image_id"]
        records = get_records_by_image_id(all_data, image_id)
        image_label = records[0]
        comment_label = records[-1]

        for attribute_key, label in image_label["label"].items():
            if filter_dataset(image_label, comment_label, attribute_key, label):
                rows.append(
                    {
                        "image_id": image_id,
                        "attribute": attribute_key,
                        "hardness": label["hardness"],
                        "certainty": label["certainty"],
                        "information_level": label["information_level"],
                        "others": False,
                        "gt": label["estimate"],
                    }
                )

            elif attribute_key == "others":
                for other_attribute, other_label in label.items():
                    rows.append(
                        {
                            "image_id": image_id,
                            "attribute": other_attribute,
                            "hardness": other_label["hardness"],
                            "certainty": other_label["certainty"],
                            "information_level": other_label["information_level"],
                            "others": True,
                            "gt": other_label["estimate"],
                        }
                    )

    df = pd.DataFrame(rows)
    df["humans"] = df["image_id"].apply(lambda x: humans[x])

    df.to_csv(f"{path}datapoints.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Label-Prediction comparison by human")

    parser.add_argument(
        "--path",
        type=str,
        help="dataset folder path e.g. ../dataset/",
        default="../dataset/",
    )
    args = parser.parse_args()

    generate_df(args.path)
