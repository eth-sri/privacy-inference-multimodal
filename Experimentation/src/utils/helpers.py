import base64
import re


def zip_files():
    import os
    import zipfile

    from src.utils.parse import parse_jsonl

    with open("../backend/data/labels/reviews2.jsonl", "r") as file:
        labels_lines = file.read()

    all_data = parse_jsonl(jsonl_content=labels_lines)

    full_image_ids = []
    for idx, data in enumerate(all_data):
        full_image_ids.append(data["datapoint"]["image_id"])

    full_image_ids = list(set(full_image_ids))

    image_files = [f"{image_id}.jpg" for image_id in full_image_ids]

    # image_files = ['image1.jpg', 'image2.png', 'image3.gif']  # Add your image filenames here
    folder_path = (
        "../backend/data/images/"  # Update this to the path of your images folder
    )
    output_zip = "images.zip"

    with zipfile.ZipFile(output_zip, "w") as zipf:
        for image in image_files:
            image_path = os.path.join(folder_path, image)
            if os.path.isfile(image_path):
                zipf.write(image_path, arcname=image)
            else:
                print(f"File {image} does not exist and will be skipped.")

    print(f"Zip file created: {output_zip}")


def extract_numbers(input_str):
    # This regex pattern looks for one or two groups of digits potentially separated by a hyphen
    # It also handles any text surrounding the numbers
    pattern = r"(\d+)(?:-(\d+))?"
    matches = re.findall(pattern, input_str)

    # If no matches are found, return None
    if not matches:
        return None

    # Since findall will return a list of tuples, we handle each case accordingly
    results = []
    for match in matches:
        # Extract numbers from match groups
        start, end = match
        # If there is no second number, it means the input was a single number.
        # Otherwise, we consider the number interval.
        results.append(start if not end else f"{start}-{end}")

    # If only one match, return just that match; otherwise return the list of matches
    return results[0] if len(results) == 1 else results


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
