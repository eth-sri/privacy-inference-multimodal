from typing import Dict

from pydantic import BaseModel


class AttributeDict(BaseModel):
    estimate: str
    information_level: int
    hardness: int
    certainty: int


class Attributes(BaseModel):
    placeOfImage: AttributeDict
    location: AttributeDict
    sex: AttributeDict
    age: AttributeDict
    occupation: AttributeDict
    placeOfBirth: AttributeDict
    maritalStatus: AttributeDict
    income: AttributeDict
    educationLevel: AttributeDict
    others: Dict[str, AttributeDict]

    def are_all_estimates_empty(self):
        attributes = [
            self.placeOfImage,
            self.location,
            self.sex,
            self.age,
            self.occupation,
            self.placeOfBirth,
            self.maritalStatus,
            self.income,
            self.educationLevel,
        ]
        return all(attribute.estimate == "" for attribute in attributes)


class Datapoint(BaseModel):
    # row_idx: int
    image_id: str
    author: str
    image_url: str
    raw_caption: str
    caption: str
    subreddit: str
    score: int
    created_utc: str
    permalink: str


class Label(BaseModel):
    datapoint: Datapoint
    label: Attributes
    user: str
    time: int


class Message(BaseModel):
    messages: list
    username: str


class Human(BaseModel):
    human: int
    image_id: str
