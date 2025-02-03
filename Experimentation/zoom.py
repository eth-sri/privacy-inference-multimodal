import argparse
import base64
import concurrent.futures
import glob
import json
import os
import re
import time
from io import BytesIO
from pathlib import Path

from PIL import Image
from src.utils.compare import compare_label
from src.utils.helpers import encode_image
from src.utils.llm_calls import get_response
from src.utils.parse import get_records_by_image_id, parse_jsonl, parse_jsonl_unique
from src.utils.prompts import (
    attribute_specific_prompt_single,
    attribute_specific_prompt_zoom,
    attribute_specific_prompts,
)
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Label-Prediction comparison by human")

parser.add_argument(
    "--computation",
    type=str,
    help="Async or parallel sync computation",
    choices=["async", "parallel"],
    default="parallel",
)

parser.add_argument(
    "--attribute", type=str, help="which attribute to ask for?", default="location"
)

parser.add_argument(
    "--model_responses",
    type=str,
    help="folder, where model responses are stored.",
    default="./model_responses/zoom",
)

args = parser.parse_args()

computation = args.computation
model_responses = args.model_responses

model = "gpt-4-1106-preview"
vlm_model = "gpt-4-1106-vision-preview"
retries = 2

with open("dataset/dataset.jsonl", "r") as file:
    json_lines = file.read()


all_data = parse_jsonl(json_lines)
parsed_data = parse_jsonl_unique(json_lines)

full_image_ids = []
for idx, data in enumerate(all_data):
    full_image_ids.append(data["datapoint"]["image_id"])

full_image_ids = list(set(full_image_ids))

# The folder in which you want to search for JSON files
folder_path = "model_responses/zoom"

# Use glob.glob() to find all the json files
json_files = glob.glob(os.path.join(folder_path, "*.json"))

# This returns the full paths; if you want just filenames, you'd need to extract them
json_filenames = set([os.path.basename(fp).split("_")[0] for fp in json_files])

# Now json_filenames contains only the file names
print(json_filenames)

# Filter out the json file names from the other_files list
image_ids = [file for file in full_image_ids if file not in json_filenames][:10]
image_ids = [file for file in full_image_ids if file not in json_filenames]

image_generic_path = "dataset/images/{image_id}.jpg"

with open("performances/image_performance_gpt4v_complex_.json", "r") as file:
    performance = json.load(file)

tasks = []

for image_id in image_ids:
    records = get_records_by_image_id(all_data, image_id)
    image_record = records[0]
    comment_record = records[-1]
    for key, value in performance.items():
        for key2, value2 in value.items():
            if "true_pred" in value2 and key2 == args.attribute and image_id == key:

                image_estimate = image_record["label"][key2]["estimate"]
                image_hardness = image_record["label"][key2]["hardness"]
                image_certainty = image_record["label"][key2]["certainty"]
                image_info_level = image_record["label"][key2]["information_level"]

                comment_hardness = comment_record["label"][key2]["hardness"]
                comment_certainty = comment_record["label"][key2]["certainty"]
                comment_info_level = comment_record["label"][key2]["information_level"]
                comment_estimate = comment_record["label"][key2]["estimate"]
                if image_hardness > 0 and compare_label(
                    gt_image=image_estimate,
                    gt_comments=comment_estimate,
                    attribute=key2,
                ):
                    if image_info_level > 0:
                        # print('info level', image_id, attribute_key)
                        continue
                    tasks.append((key, key2))

print(f"#tasks {len(tasks)}")


def predict_single_attribute_w_zoom(
    image_id: str, attribute: str, max_retries=2, backoff_factor=1
):

    image_path = image_generic_path.format(image_id=image_id)
    img = Image.open(image_path)

    base64_image = encode_image(image_path=image_path)

    if attribute in attribute_specific_prompts:
        attribute_prompt = attribute_specific_prompts[attribute]
    else:
        attribute_prompt = attribute

    retries = 0
    # while retries < max_retries:
    try:

        if attribute in attribute_specific_prompts:
            attribute_prompt = attribute_specific_prompts[attribute]
        else:
            attribute_prompt = attribute

        PROMPT_MESSAGES = [
            {
                "role": "system",
                "content": attribute_specific_prompt_zoom["system1"],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                    {
                        "type": "text",
                        "text": attribute_specific_prompt_zoom["header_new2"].format(
                            target_attribute_str=attribute
                        ),
                    },
                ],
            },
        ]
        params = {
            "model": vlm_model,
            "messages": PROMPT_MESSAGES,
            "max_tokens": 1000,
            "temperature": 0,
            "stream": False,
        }

        result = get_response(**params)

        image_description = result.choices[0].message.content

        pattern = r"\bbounding_box\((\d+)%,\s*(\d+)%,\s*(\d+)%,\s*(\d+)%\)"

        # Performing the search to find all instances and parse the numbers
        matches = re.findall(pattern, image_description)

        # Converting each match from strings to integers
        bounding_boxes = [tuple(map(int, match)) for match in matches]

        width, height = img.size
        # bbox = (30*width/100, 20*height/100, 70*width/100, 40*height/100)
        # cropped_image = img.crop(bbox)

        cropped_images = []

        for bbox in bounding_boxes:
            margin_x = (40 - (bbox[2] - bbox[0])) / 2
            margin_y = (40 - (bbox[3] - bbox[1])) / 2
            if margin_x < 0:
                margin_x = 0
            if margin_y < 0:
                margin_y = 0

            edge_margin = 4
            limits_low = 0
            limits_high = 100

            left = bbox[0] - margin_x
            right = bbox[2] + margin_x
            if left < (limits_low + edge_margin):
                right = right - (left - edge_margin)
                left = limits_low + edge_margin
            elif 100 - right < (limits_low + edge_margin):
                left = left + (100 - (right + edge_margin))
                right = limits_high - edge_margin

            upper = bbox[1] - margin_y
            lower = bbox[3] + margin_y
            if upper < (limits_low + edge_margin):
                lower = lower - (upper - edge_margin)
                upper = limits_low + edge_margin
            elif 100 - lower < (limits_low + edge_margin):
                upper = upper + (100 - (lower + edge_margin))
                lower = limits_high - edge_margin
            bbox_adjusted = (
                left * width / 100,
                upper * height / 100,
                right * width / 100,
                lower * height / 100,
            )
            cropped_image = img.crop(bbox_adjusted)

            buffered = BytesIO()
            cropped_image.save(buffered, format="PNG")
            cropped_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            cropped_images.append(cropped_img_str)

        PROMPT_MESSAGES = [
            {
                "role": "system",
                "content": attribute_specific_prompt_zoom["system1"],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                    {
                        "type": "text",
                        "text": attribute_specific_prompt_zoom["header_new2"].format(
                            target_attribute_str=attribute
                        ),
                    },
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": image_description},
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{cropped_base64_image}"
                        },
                    }
                    for cropped_base64_image in cropped_images
                ]
                + [
                    {
                        "type": "text",
                        "text": attribute_specific_prompt_zoom["header2"]
                        + "\n\n"
                        + attribute_specific_prompts["free_text"]
                        + "\n"
                        + attribute_prompt,
                    },
                ],
            },
        ]
        params = {
            "model": vlm_model,
            "messages": PROMPT_MESSAGES,
            "max_tokens": 1000,
            "temperature": 0,
            "stream": False,
        }

        chat_completion = get_response(**params)

        return chat_completion
    except Exception as e:
        print(e)


def predict_parallel_single_attribute(image_paths, save_path):

    print(f"#images: {len(image_paths)}")
    max_workers = 5

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_image = {
            executor.submit(predict_single_attribute_w_zoom, image_path, attribute): (
                image_path,
                attribute,
            )
            for image_path, attribute in tasks
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
                    path = save_path / Path(f"{image}_{attribute}.json")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("w") as file:
                        file.write(data.model_dump_json())
                    pass
                else:
                    print(f"{image}: Retries exceeded.")
            except Exception as exc:
                print(f"{image} generated an exception: {exc}")


if __name__ == "__main__":

    predict_parallel_single_attribute(image_ids, save_path=model_responses)
