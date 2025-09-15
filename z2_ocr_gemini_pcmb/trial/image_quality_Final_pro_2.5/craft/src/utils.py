import boto3

# from PIL import Image
# from io import BytesIO
import numpy as np
import os
import requests
import cv2


def download_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise Exception("Failed to decode image")
        return image
    except Exception as e:
        raise Exception(f"Error downloading image from URL: {str(e)}")


# def download_image(image_url):
#     try:
#         response = requests.get(image_url)
#         response.raise_for_status()
#         return np.array(Image.open(BytesIO(response.content)))
#     except Exception as e:
#         raise Exception(f"Error downloading image from URL: {str(e)}")


def download_model(bucket_name, model_path):
    weights_dir = "weights"
    if not os.path.exists(weights_dir):
        os.makedirs(weights_dir)

    s3_client = boto3.client("s3")
    model_filename = model_path.split("/")[-1]
    local_path = os.path.join(weights_dir, model_filename)
    if not os.path.exists(local_path):
        try:
            print(
                f"Downloading {model_filename} from S3 bucket: {bucket_name} to {local_path}"
            )
            s3_client.download_file(bucket_name, model_path, local_path)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download model.pt: {e}")
            return None
    return local_path


def download_model_dir(bucket_name, model_dir):
    base_dir = os.path.expanduser("~/.paddleocr")
    whl_dir = os.path.join(base_dir, "whl")
    if not os.path.exists(whl_dir):
        os.makedirs(whl_dir)

        s3_client = boto3.client("s3")
        print(
            f"Downloading model files from S3 bucket: {bucket_name}, prefix: {model_dir}"
        )

        # List all objects in the model directory
        paginator = s3_client.get_paginator("list_objects_v2")
        objects = paginator.paginate(Bucket=bucket_name, Prefix=model_dir)

        # Download each file while preserving structure inside whl
        for page in objects:
            for obj in page.get("Contents", []):
                s3_path = obj["Key"]
                # Remove the prefix path up to 'whl/'
                if "/whl/" in s3_path:
                    relative_path = s3_path.split("/whl/", 1)[1]
                    if relative_path:  # Skip if it's just the directory itself
                        # Create the local path under whl directory
                        local_path = os.path.join(whl_dir, relative_path)
                        local_dir = os.path.dirname(local_path)

                        if not os.path.exists(local_dir):
                            os.makedirs(local_dir)

                        print(f"Downloading: {relative_path}")
                        s3_client.download_file(bucket_name, s3_path, local_path)


def download_image_from_s3(image_path, bucket_name):
    try:
        s3_client = boto3.client("s3")
        print(f"Downloading image from S3: {image_path} in bucket: {bucket_name}")
        response = s3_client.get_object(Bucket=bucket_name, Key=image_path)
        image_data = response["Body"].read()
        img = Image.open(BytesIO(image_data))
        return np.array(img)
    except Exception as e:
        raise Exception(f"Error downloading image from S3: {str(e)}")