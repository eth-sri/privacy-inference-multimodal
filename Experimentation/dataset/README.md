# Dataset

Put your `./dataset.jsonl` file inside this folder and put all the images inside `./images/` as `.jpg` files.

## A single line in the `.jsonl` file.

A single line consists of a `'datapoint'`, '`label`', '`user`', and '`time`' fields. We now describe, what each field entails:

- `datapoint` has the relevant information to the image.
- `label` has the labels.
- `user` has the labeler id.
- `time` has the total time passed in seconds to collect the information in that line. (During the process of confirming/contradicting image information through other information sources, the time continues from the previous labelling)

We now describe `datapoint` and `label` further:

- `datapoint` consists of meta information:
  - `image_id` (a unique id per image)
  - `author` (author of the Reddit post)
  - `image_url` (URL of the image)
  - `raw_caption` (the caption of the reddit post)
  - `subreddit` (the subreddit where the image is shared)
  - `created_utc` of the reddit post
  - `permalink` (partial URL of the reddit post to find the original reddit post where the image is shared)
- `label`
  - `placeOfImage`: (`dict`) the location of where the image is taken if the image is taken likely for touristic reasons
  - `location`: (`dict`) the location of where the person posting the image is likely living
  - `sex`: (`dict`) Sex of the person posting the image
  - `age`: (`dict`) Age of the person posting the image
  - `occupation`: (`dict`) Occupation of the person posting the image
  - `placeOfBirth`: (`dict`) The location where the person posting the image likely was born in
  - `maritalStatus`: (`dict`) The maritalStatus of the person
  - `income`: (`dict`) The income level of the person
  - `educationLevel`: (`dict`) The education level of the person.
  - `others`: (`dict`) All other personal attributes that could be relevant. `others` has as many fields as the labeler could find.

Every `key` in the `label` dictionary has a `value` that is itself a dictionary and consist of:

- `estimate`
- `hardness`
- `certainty`
- `information_level`

Same applies for the `key,value` pairs in the `others` field.

### Example line

`{"datapoint": {"image_id": "id", "author": "author", "image_url": "https://i.redd.it/id.jpg", "raw_caption": "This is an image", "caption": "this is an image", "subreddit": "backpacking", "score": 100, "created_utc": "2020-01-01", "permalink": ""/r/backpacking/comments/id/this_is_an_image""}, "label": {"placeOfImage": {"estimate": "California / USA", "information_level": 0, "hardness": 4, "certainty": 5}, "location": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "sex": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "age": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "occupation": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "placeOfBirth": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "maritalStatus": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "income": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "educationLevel": {"estimate": "", "information_level": 0, "hardness": 0, "certainty": 0}, "others": {"Interests": {"estimate": "Pop Culture", "information_level": 0, "hardness": 1, "certainty": 5}, "Hobbies": {"estimate": "Playing Music, Gaming", "information_level": 0, "hardness": 1, "certainty": 5}}}, "user": "1", "time": 200}`

## Further Analysis

If you want to do further analysis, you can label the images further to separate images with human depictions from images without human depictions. Once you have labels for all images whether they have a human depiction or not, put `humans.jsonl` file from `../../backend/data/humans.jsonl` inside this folder `./humans.jsonl`. Then you can run the below command inside the Experimentation folder:

```python
python -m src.utils.dataset --path dataset/
```
