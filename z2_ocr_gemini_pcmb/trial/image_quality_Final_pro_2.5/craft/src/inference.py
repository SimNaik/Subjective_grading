# Text detection service using CRAFT model

import time
import torch
from craft_text_detector import load_craftnet_model
from craft_helper import process_image_and_detect_text
from src.utils import download_image

def initialize_model():
    try:
        craft_net = load_craftnet_model(cuda=torch.cuda.is_available())
        # Warm up model
        start_time = time.time()
        process_image_and_detect_text(
            image="warmup_image.jpg",
            model=craft_net,
        )
        print("Warmup done", time.time() - start_time)

        return craft_net
    except Exception as e:
        raise Exception(f"Failed to initialize Text Detection model: {str(e)}")


text_detection_model = initialize_model()


def model_inference(input_data, model=text_detection_model):
    try:
        # Extract input parameters
        #image_url = input_data.get("image_url")
        #image = download_image(image_url)
        image = input_data.get("image")

        # Model parameters
        text_threshold = input_data.get("text_threshold", 0.1) # changed from 0.3 to 0.1 
        low_text = input_data.get("low_text", 0.1) # changed from 0.2 to 0.1
        long_size = input_data.get("long_size", 720)
        link_threshold = 0.1

        # Process image using craft helper
        boxes, confs = process_image_and_detect_text(
            image=image,
            model=model,
            text_threshold=text_threshold,
            link_threshold=link_threshold,
            low_text=low_text,
            long_size=long_size,
        )

        # Prepare response
        response = {
            #"image_source": image_url,
            "image_source": image,
            "text_regions": [
                {"confidence": conf, "bbox": box.tolist()}
                for box, conf in zip(boxes, confs)
            ],
        }

        return {
            "status": 200,
            "model_response": response,
        }

    except Exception as e:
        return {"error": str(e), "status": "error"}