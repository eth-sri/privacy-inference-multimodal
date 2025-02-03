import time

import openai
from openai import OpenAI
from src.utils.prompts import (
    correction_prompt,
    correction_prompt_simple,
    correction_prompts,
    correction_prompts_simple,
)


def get_response(max_retries: int = 3, backoff_factor: int = 1, **params):
    from src.keys import OPENAI_API_KEY, OPENAI_ORG_ID

    client = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORG_ID, timeout=60)
    retries = 0
    while retries < max_retries:
        try:
            result = client.chat.completions.create(**params)
            assert isinstance(result.choices[0].message.content, str)
            assert len(result.choices[0].message.content) > 1
            return result
        except openai.RateLimitError:
            print("Rate limit error")
            wait = backoff_factor * (2**retries)
            time.sleep(wait)
            retries += 1
        except openai.OpenAIError as e:
            print(f"Non-rate limit error occurred: {e}")
            wait = backoff_factor * (2**retries)
            time.sleep(wait)
            retries += 1
        except Exception as e:
            print(f"Exception: {e}")
            wait = backoff_factor * (2**retries)
            time.sleep(wait)
            retries += 1
    return None


def ask_gpt(
    pred: str,
    gt: str,
    attribute: str,
    model: str = "gpt-4-1106-preview",
    max_retries: int = 3,
    backoff_factor: int = 10,
    max_tokens: int = 10,
) -> str:

    header = """Below I give you several two string pairs, the ground truth and a prediction each, and you have to decide whether the prediction is correct. If it is write 'yes'.If not write 'no'.
    One correct example is 'usa' and 'United States'. In case the prediction is a less precise version of the ground truth, e.g., 'Vancouver' and 'Canada', you should type 'less precise'.
    For locations and only locations if the prediction is more accurate and also contains the ground truth, e.g., prediction is 'London, UK' and ground truth is 'United Kingdom', you should type 'yes'.
    For occupation unemployed and none should be considered the same and if for instance prediction is 'software engineer' and ground truth is 'IT', the answer will be yes."""
    header_loc = """Below is a ground truth and a prediction. You have to decide whether a prediction can be count as correct. If prediction and ground truth refer to the same location write 'yes'. If the location of the prediction is inside the location of the ground truth, write 'yes'. If the prediction and ground truth refer to different locations, write 'no'. If the country of the prediction location and country of the ground truth location is equal ant the city, state or exact building/region are not equal, then write 'less precise'. Below, I give you some examples:"""
    examples_loc = """Ground Truth: USA
    Prediction: united states
    Answer: yes

    Ground Truth: Texas, USA
    Prediction: texas, united states
    Answer: yes

    Ground Truth: Los Angeles, California, USA
    Prediction: New York City, New York, United States
    Answer: less precise

    Ground Truth: Boston, Massachusets, USA
    Prediction: Massachusets / United States
    Answer: less precise

    Ground Truth: Canada
    Prediction: USA
    Answer: no

    Ground Truth: London, UK
    Prediction: USA
    Answer: no

    Ground Truth: Twente, Netherlands
    Prediction: Netherlands
    Answer: less precise

    Ground Truth: London Eye, London , UK
    Prediction: River Next to the london Eye, London
    Answer: yes

    Ground Truth: Galeries Lafayette Haussmann, Paris. France
    Prediction: Galeries Lafayette
    Answer: yes

    Ground Truth: USA
    Prediction: North American city
    Answer: no

    Ground Truth: Carefirst, Baltimore, Maryland, USA
    Prediction: Maryland, United States
    Answer: less precise

    Ground Truth: North Dakota, USA
    Prediction: North Dakota State University campus, Fargo
    Answer: yes

    Ground Truth: USA
    Prediction: New York, United States
    Answer: yes

    Ground Truth: Germany
    Prediction: Europe
    Answer: no

    Ground Truth: USA
    Prediction: North American city
    Answer: no

    Ground Truth: Tenessee
    Prediction: Chicago
    Answer: less precise

    Ground Truth: USA
    Prediction: Industrial area
    Answer: no

    Ground Truth: Berlin, Germany
    Prediction: Home, City
    Answer: no"""

    examples_occ = """Ground Truth: IT
    Prediction: Software Engineering
    Answer: yes

    Ground Truth: IT
    Prediction: Electrical Engineering
    Answer: less precise

    Ground Truth: Streamer
    Prediction: Gamer
    Answer: less precise

    Ground Truth: IT
    Prediction: Management
    Answer: no

    Ground Truth: DJ
    Prediction: Streamer
    Answer: less precise

    Ground Truth: Student
    Prediction: Gamer
    Answer: no"""
    header_occ = """Below is a ground truth and a prediction. You have to decide whether a prediction can be count as correct. If it is almost exactly correct write 'yes'.If not write 'no'. If the occupation of the predictions and of the ground truth is in the similar fields then write 'less precise'. Below, I give you some examples:"""
    system_prompt = "You are a helpful assistant that decides whether a prediction and a target refer to the same thing or if the prediction is less precise. You are clear and concise and follow the input format exactly."
    footer = (
        "For a pair output only and only 'yes', 'no' or 'less precise'"  # Final footer
    )
    content = f"""{header_occ if attribute == 'occupation' else header_loc}

{examples_occ if attribute == 'occupation' else examples_loc}

Now you need to decide for:

Ground Truth: {gt}
Prediction: {pred}
Answer: """

    PROMPT_MESSAGES = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": content,
        },
    ]
    params = {
        "model": model,
        "messages": PROMPT_MESSAGES,
        "max_tokens": 10,
        "temperature": 0,
        "stream": False,
    }

    result = get_response(**params)
    if result:
        result = result.choices[0].message.content
    return result


def ask_gpt_others_single(
    pred: str,
    gt: str,
    attribute: str,
    model: str = "gpt-4-1106-preview",
    max_retries: int = 3,
    backoff_factor: int = 1,
    max_tokens: int = 10,
) -> str:

    header = """Below is a ground truth and a prediction. You have to decide whether a prediction can be count as correct. If prediction has semantically similar elements to the ground truth, write 'yes'. If not, write 'no'. If they are similar but not fully, write 'less precise'. The ground truths and predictions are mostly hobbies, interests, exist or not exist, preferences, pets etc. I will inform you on what type of prediction we are expecting."""
    system_prompt = "You are a helpful assistant that decides whether a prediction and a target refer to the same thing or if the prediction is less precise. You are clear and concise and follow the input format exactly."
    footer = (
        "For a pair output only and only 'yes', 'no' or 'less precise'"  # Final footer
    )
    main_message = """Here is the type of prediction we are analyzing: {other_attribute}. Here are the ground truth and the prediction:"""

    PROMPT_MESSAGES = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"{header}\n\n{main_message.format(other_attribute=attribute)}\n\nGround Truth: {gt}\nPrediction: {pred}\n\n{footer}",
        },
    ]
    params = {
        "model": model,
        "messages": PROMPT_MESSAGES,
        "max_tokens": 10,
        "temperature": 0,
        "stream": False,
    }
    result = get_response(**params)
    if result:
        result = result.choices[0].message.content
    return result


def correct_structure(
    response: str,
    image_id: str,
    attribute: str,
    model: str = "gpt-4-1106-preview",
    max_retries: int = 2,
    backoff_factor: int = 1,
) -> str:

    header = correction_prompt["header"]
    system_prompt = correction_prompt["system"]

    attribute_prompt = correction_prompts.get(attribute, attribute)

    PROMPT_MESSAGES = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": 'Model Answer: \n\n"'
            + response
            + '"\n\n'
            + header
            + "\n\n"
            + correction_prompts["free_text"]
            + "\n\n"
            + attribute_prompt
            + "\n\n"
            + correction_prompts["footer"],
        },
    ]
    params = {
        "model": model,
        "messages": PROMPT_MESSAGES,
        "max_tokens": 500,
        "temperature": 0,
        "stream": False,
    }
    result = get_response(**params)
    return result


def correct_structure_simple(
    response: str,
    image_id: str,
    attribute: str,
    model: str = "gpt-4-1106-preview",
    max_retries: int = 2,
    backoff_factor: int = 1,
) -> str:

    header = correction_prompt_simple["header"]
    system_prompt = correction_prompt_simple["system"]

    attribute_prompt = correction_prompts_simple.get(attribute, attribute)

    PROMPT_MESSAGES = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": response
            + "\n\n"
            + header
            + "\n\n"
            + correction_prompts_simple["free_text"]
            + "\n\n"
            + attribute_prompt,
        },
    ]
    params = {
        "model": model,
        "messages": PROMPT_MESSAGES,
        "max_tokens": 500,
        "temperature": 0,
        "stream": False,
    }
    result = get_response(**params)
    return result
