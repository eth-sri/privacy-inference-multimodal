import io
import json
import random
import urllib
from datetime import datetime
from pathlib import Path
from typing import Union

import PIL.Image
import requests
from datasets.utils.file_utils import get_datasets_user_agent
from datatypes import Attributes, Human, Label, Message
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from globals import subreddits_to_sample_from_manual


def get_date(timestamp):
    # Convert Unix timestamp to a datetime object
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")


# Set up the path where the JSON files are located
json_directory = Path("../../Datasets/RedCaps/redcaps_v1.0_annotations/annotations")


def read_jsonl_to_list(file_path):
    path = Path(file_path)
    if path.is_file():
        with path.open("r") as file:
            return [json.loads(line) for line in file]
    else:
        return []


def read_json(filename: str) -> list:
    with open(filename, "r") as file:
        return json.load(file)


file_path = "data/labels/dataset.jsonl"
human_path = "data/labels/humans.jsonl"
reviews = read_jsonl_to_list(file_path)
print("read files")

USER_AGENT = get_datasets_user_agent()


def fetch_single_image(image_url, image_id, timeout=None, retries=0):
    image_path = Path("data/images") / Path(image_id + ".jpg")
    if image_path.is_file():
        # Read the image file into bytes
        image = image_path.read_bytes()
    else:
        for _ in range(retries + 1):
            try:
                request = urllib.request.Request(
                    image_url,
                    data=None,
                    headers={"user-agent": USER_AGENT},
                )
                with urllib.request.urlopen(request, timeout=timeout) as req:
                    # image = PIL.Image.open(io.BytesIO(req.read()))
                    image = req.read()
                break
            except Exception as e:
                print(e)
                image = None
    return image


def fetch_single_row_local():
    sample_subreddit = random.sample(subreddits_to_sample_from_manual, 1)[0]
    print("sample subreddit", sample_subreddit)
    group_files = json_directory.glob(f"{sample_subreddit}_20[1-2][0-9].json")
    print("group files", group_files)

    # Concatenate all the annotations lists
    annotations = []
    for file_path in group_files:
        # print('file path', file_path)
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            annotations.extend(data["annotations"])

    sample_size = 1
    if len(annotations) >= sample_size:
        random_sample = random.sample(annotations, sample_size)
    else:
        print(f"Annotations {len(annotations)}")
        raise ValueError(
            "Sample size exceeds the total number of annotations available"
        )
    return random_sample[0]


app = FastAPI()

origins = ["http://localhost:4000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_form_data_empty(formData: Attributes) -> bool:
    return all(value == "" for value in formData.model_dump().values())


@app.post("/submit_form/")
async def receive_form(data: Label):
    form_data = data.label
    user = data.user
    time = data.time
    print(user, time)
    all_estimates_empty = form_data.are_all_estimates_empty()
    if not all_estimates_empty:
        with open(file_path, "a") as file:
            file.write(data.model_dump_json() + "\n")

    return {"message": "Form data received successfully"}


@app.post("/submit_human/")
async def receive_human(data: Human):
    human = data.human
    image_id = data.image_id
    print(image_id, human)
    with open(human_path, "a") as file:
        file.write(json.dumps({image_id: human}) + "\n")

    return {"message": "Human data received successfully"}


@app.post("/skip/")
async def receive_form_skip(data: Label):
    form_data = data.label
    user = data.user
    time = data.time
    datapoint = data.datapoint
    print(user, time)
    all_estimates_empty = form_data.are_all_estimates_empty()
    if all_estimates_empty:
        with open("data/skipped/skipped.jsonl", "a") as file:
            file.write(datapoint.model_dump_json() + "\n")

    return {"message": "Form data received successfully"}


@app.get("/get_image/")
async def get_image(image_url: str, image_id: str):
    image = fetch_single_image(image_url, image_id, 2, 3)
    # Specify the file path
    file_path = Path(f"data/images/{image_id}.jpg")
    if not file_path.exists():
        print("Trying to save!")
        try:
            with PIL.Image.open(io.BytesIO(image)) as im:
                im.save(f"data/images/{image_id}.jpg")
                print("Saved!")
        except Exception:
            print("Saving failed!")
    return Response(image, media_type="image/jpeg")


@app.get("/get_datapoint/")
async def get_datapoint():
    data = fetch_single_row_local()
    datapoint = {}
    if data:
        datapoint = data
    return {"datapoint": datapoint}


@app.get("/get_label/")
async def get_labelled_datapoint(index: int):
    return {"review": reviews[index]}


@app.get("/get_labels_length/")
async def get_dataset_length():
    return {"length": len(reviews)}


@app.get("/reddit/")
async def get_reddit_data(username: str, start_year: int = 2008, end_year: int = 2022):
    try:
        # Replace 'RedditApp/0.1 by RedditUsername' with your own User-Agent
        user_agent = "RedditApp/0.1 by RedditUsername"

        # The Reddit API endpoint for a user's comments, with a maximum limit of 100
        url = f"https://www.reddit.com/user/{username}/comments.json?limit=100"

        # Send a GET request to the Reddit API
        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            comments = []
            # Iterate through each comment in the response
            for comment_data in data["data"]["children"]:
                comment = comment_data["data"]
                text = comment["body"]  # The text of the comment
                subreddit = comment["subreddit"]  # The subreddit the comment is from
                created_utc = get_date(
                    comment["created_utc"]
                )  # The creation date of the comment
                comment_element = {
                    "subreddit": f"/r/{subreddit}",
                    "date": created_utc,
                    "comment": text,
                }
                comments.append(comment_element)
                # print(f"Subreddit: /r/{subreddit}, Date: {created_utc}, Comment Text: {text}\n")
            with open(f"data/comments/{username}.jsonl", "w") as jsonl_file:
                for entry in comments:
                    json_line = json.dumps(entry) + "\n"
                    jsonl_file.write(json_line)

            return {"comments": comments}
        else:
            print(f"Error: Status code {response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reddit_local/")
async def get_local_reddit_data(
    username: str, start_year: int = 2008, end_year: int = 2022
):
    try:
        comments = read_jsonl_to_list(f"data/comments/{username}.jsonl")
        return {"comments": comments}
    except Exception as e:
        raise e


@app.get("/get_chat/")
async def get_chat(username: str, start_year: int = 2008, end_year: int = 2022):
    try:
        messages = read_json(f"data/chats/{username}.json")
        return {"messages": messages}
    except Exception as e:
        raise e


@app.post("/save_chat")
async def store_messages(message: Message):
    print(message)
    with open(f"data/chats/{message.username}.json", "w") as json_file:
        json_content = json.dumps(message.messages)
        json_file.write(json_content)
    return {"message": "Successfully saved chat"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
