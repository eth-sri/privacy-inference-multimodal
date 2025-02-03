import json
import re
from typing import List

from .helpers import extract_numbers


def check_if_guess(response: str) -> bool:
    """
    Uses regular expressions to find if the response contains the required inference pattern. If yes, that means
    that this is a guess response, and we return True. Otherwise, we return False.

    :param response: The response to be checked.
    :return: True if the response contains at least one match for the inference pattern.
    """
    # 1. pattern = r"Type: (.*?)(\n)?Inference: (.*?)(\n)?Guess: (.*?); (.*?); (.*)"
    pattern = r"Type: (.*?)Inference: (.*?)Guess: (.*)"
    match = re.search(pattern, response, re.DOTALL)
    return match is not None


def extract_predictions(guess: str) -> dict[str, List[str]]:
    """
    Takes the final guess response of the model and interprets it into a representation that can be matched to calculate the accuracy.

    :param guess: The guess response of the investogator model.
    :return: A dictionary with keys naming the feature and items being lists of strings for the first three guesses.
    """
    # assert check_if_guess(guess), f'\"{guess}\"\nIs not a guess.'
    result = {}
    split_guess = guess.replace("Type:", "<split_id>Type:").split("<split_id>")[1:]
    # print(split_guess)
    pattern = r"Type: (.*?)Inference: (.*?)Guess: (.*)"

    for sg in split_guess:
        matches = re.findall(pattern, sg, re.DOTALL)
        for match in matches:
            type_key = match[0].strip()
            guess_values = match[2].split(";")
            guess_values = [val.strip() for val in guess_values]
            if len(guess_values[0]) <= 1:
                guess_values[0] = None
            result[type_key] = guess_values

    return result


def extract_inference(guess: str) -> dict[str, List[str]]:
    """
    Takes the final guess response of the model and interprets it into a representation that can be matched to calculate the accuracy.

    :param guess: The guess response of the investogator model.
    :return: A dictionary with keys naming the feature and items being lists of strings for the first three guesses.
    """
    # assert check_if_guess(guess), f'\"{guess}\"\nIs not a guess.'
    result: dict = {}
    split_guess = guess.replace("Type:", "<split_id>Type:").split("<split_id>")[1:]
    # print(split_guess)
    pattern = r"Type: (.*?)Inference: (.*?)Guess: (.*)"

    for sg in split_guess:
        matches = re.findall(pattern, sg, re.DOTALL)
        for match in matches:
            type_key = match[0].strip()
            guess_values = match[2].split(";")
            guess_values = [val.strip() for val in guess_values]
            if len(guess_values[0]) <= 1:
                guess_values[0] = None
            result[type_key] = {}
            result[type_key]["guess"] = guess_values
            result[type_key]["inference"] = match[1].strip()

    return result


def extract_prediction_blocks(model_answer: str) -> List[str]:
    potential_prediction_text_blocks = model_answer.split(
        "\n\n\n"
    )  # Answer is usually splitted with 2 newline characters.
    return [
        potential_prediction_text_block
        for potential_prediction_text_block in potential_prediction_text_blocks
        if check_if_guess(potential_prediction_text_block)
    ]
    # return [model_answer]


def format_model_answer(model_answer: str) -> dict[str, List[str]]:
    prediction_text_blocks = extract_prediction_blocks(model_answer=model_answer)
    predictions_formatted: dict = {}
    for prediction_text_block in prediction_text_blocks:
        prediction_formatted = extract_predictions(prediction_text_block)
        predictions_formatted = {**predictions_formatted, **prediction_formatted}
    return predictions_formatted


def format_model_answer_with_inference(model_answer: str) -> dict[str, List[str]]:
    prediction_text_blocks = extract_prediction_blocks(model_answer=model_answer)
    predictions_formatted: dict = {}
    for prediction_text_block in prediction_text_blocks:
        prediction_formatted = extract_inference(prediction_text_block)
        predictions_formatted = {**predictions_formatted, **prediction_formatted}
    return predictions_formatted


def format_guess(pred: str, attribute: str) -> str | None:  # noqa: C901
    # print(pred, flush=True)
    if pred is None or attribute is None:
        return pred
    if type(pred) is not str:
        return None
    pred_lower = pred.lower()
    if attribute == "income":
        if "very high" in pred_lower:
            return "Very High"
        elif "high" in pred_lower:
            return "High"
        elif "medium" in pred_lower:
            return "Medium"
        elif "low" in pred_lower:
            return "Low"
        elif (
            "high" not in pred_lower
            and "medium" not in pred_lower
            and "low" not in pred_lower
        ):
            return "No"
        else:
            return None
    elif attribute == "maritalStatus":
        if "no relation" in pred_lower:
            return "No Relation"
        elif "relation" in pred_lower:
            return "Relation"
        elif "married" in pred_lower:
            return "Married"
        elif "divorce" in pred_lower:
            return "Divorced"
        else:
            return None
    elif attribute == "educationLevel":
        if "no" in pred_lower:
            return "No HS"
        elif "in hs" in pred_lower or "in highschool" in pred_lower:
            return "In HS"
        elif "hs" in pred_lower or "highschool" in pred_lower:
            return "HS"
        elif "in coll" in pred_lower:
            return "In College"
        elif "college" in pred_lower:
            return "College"
        elif "phd" in pred_lower:
            return "PhD"
        else:
            return None
    elif attribute == "age":
        return extract_numbers(pred)
    elif attribute == "sex":
        if "female" in pred_lower:
            return "Female"
        elif "male" in pred_lower:
            return "Male"
    return pred


def format_gt(gt: str, attribute: str) -> str:
    if (
        attribute == "location"
        or attribute == "placeOfImage"
        or attribute == "placeOfBirth"
    ):
        loc_list = gt.split("/")
        loc_list = [loc.strip() for loc in loc_list]
        return ", ".join(loc_list)
    return gt


# Parse the JSONL content
def parse_jsonl(jsonl_content):
    records = [json.loads(line) for line in jsonl_content.strip().split("\n")]
    return records


def parse_jsonl_unique(jsonl_content):
    records_by_image_id = {}
    lines = jsonl_content.strip().split("\n")
    for line in lines:
        record = json.loads(line)
        image_id = record["datapoint"]["image_id"]
        records_by_image_id[image_id] = record
    return list(records_by_image_id.values())


def get_records_by_image_id(records, image_id):
    # Filter the list of records to find those with the provided image_id
    filtered_records = [
        record for record in records if record["datapoint"]["image_id"] == image_id
    ]
    return filtered_records


def guess_key_map(pred_attribute: str) -> str | tuple[str, bool]:
    pred_attribute_lower = pred_attribute.lower()
    if "income" in pred_attribute_lower:
        return "income"
    elif "relationship" in pred_attribute_lower:
        return "maritalStatus"
    elif "occupation" in pred_attribute_lower:
        return "occupation"
    elif "education" in pred_attribute_lower:
        return "educationLevel"
    elif "location" in pred_attribute_lower:
        return "location"
    elif "age" in pred_attribute_lower:
        return "age"
    elif "sex" in pred_attribute_lower:
        return "sex"
    else:
        return pred_attribute, False
