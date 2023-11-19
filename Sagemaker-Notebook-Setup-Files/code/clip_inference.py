
import io
import torch
import clip
from PIL import Image
import json
import logging
import sys
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.transforms import ToTensor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# ENCODE_TYPE could be IMAGE or TEXT
ENCODE_TYPE = os.environ.get("ENCODE_TYPE", "TEXT")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# defining model and loading weights to it.
def model_fn(model_dir):
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.load_state_dict(torch.load(os.path.join(model_dir, 'new_clip_model.pt'), map_location=device))
    model.eval()  # Set the model to evaluation mode
    
    # Load the state dictionary from the saved .pt file
    saved_state_dict = torch.load(os.path.join(model_dir, 'new_clip_model.pt'), map_location=torch.device('cpu'))

    # Check if the state dictionaries are the same
    are_equal = all(torch.allclose(model.state_dict()[key], saved_state_dict[key]) for key in model.state_dict())

    if are_equal:
        print("State dictionaries are the same!")
    else:
        print("State dictionaries are different.")
    return {"model_obj": model, "preprocess_fn": preprocess}


def load_from_bytearray(request_body):
    
    return image

# data loading
def input_fn(request_body, request_content_type):
    assert request_content_type in (
        "application/json",
        "application/x-image",
    ), f"{request_content_type} is an unknown type."
    if request_content_type == "application/json":
        data = json.loads(request_body)["inputs"]
        print(f" Data IS :::: {data}")
    elif request_content_type == "application/x-image":
        image_as_bytes = io.BytesIO(request_body)
        data = Image.open(image_as_bytes)
    return data


# inference
def predict_fn(input_object, model):
    model_obj = model["model_obj"]
    # for image preprocessing
    preprocess_fn = model["preprocess_fn"]
    assert ENCODE_TYPE in ("TEXT", "IMAGE"), f"{ENCODE_TYPE} is an unknown encode type."

    # preprocessing
    if ENCODE_TYPE == "TEXT":
        input_ = clip.tokenize(input_object).to(device)
    elif ENCODE_TYPE == "IMAGE":
        input_ = preprocess_fn(input_object).unsqueeze(0).to(device)

    # inference
    with torch.no_grad():
        if ENCODE_TYPE == "TEXT":
            prediction = model_obj.encode_text(input_)
            print('prediction of text in model')
            print(prediction)
        elif ENCODE_TYPE == "IMAGE":
            prediction = model_obj.encode_image(input_)
            print('prediction of image in model')
            print(prediction)
    return prediction

# Serialize the prediction result into the desired response content type
def output_fn(predictions, content_type):
    assert content_type == "application/json"
    res = predictions.cpu().numpy().tolist()
    return json.dumps(res)
