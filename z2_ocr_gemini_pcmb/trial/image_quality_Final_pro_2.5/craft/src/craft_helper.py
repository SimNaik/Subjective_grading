import torch
import numpy as np
import cv2
from craft_text_detector import craft_utils, image_utils, torch_utils

def process_image_and_detect_text(
    image, model, text_threshold=0.3, link_threshold=0.5, low_text=0.2, long_size=720
):
    """
    Process an image for text detection using CRAFT model
    Args:
        image: Input image
        model: CRAFT model
        text_threshold: Text confidence threshold
        link_threshold: Link confidence threshold
        low_text: Low text confidence threshold
        long_size: Longer side size for resizing
    Returns:
        boxes: List of detected text boxes with normalized coordinates (0-1)
        confs: List of confidence scores for each box
    """
    # Preprocess image
    image = image_utils.read_image(image)
    img_resized, _, _ = image_utils.resize_aspect_ratio(
        image, long_size, interpolation=cv2.INTER_LINEAR
    )

    # Prepare input tensor
    x = image_utils.normalizeMeanVariance(img_resized)
    x = torch_utils.from_numpy(x).permute(2, 0, 1).unsqueeze(0)
    if torch.cuda.is_available():
        x = x.cuda()

    # Model inference
    with torch_utils.no_grad():
        y, _ = model(x)

    # Post-process outputs
    score_text = y[0, :, :, 0].cpu().data.numpy()
    score_link = y[0, :, :, 1].cpu().data.numpy()
    hmap_h, hmap_w = score_text.shape[:2]

    boxes_scaled, _ = craft_utils.getDetBoxes(
        score_text, score_link, text_threshold, link_threshold, low_text, poly=True
    )

    # Calculate confidence scores and normalize coordinates
    boxes_normalized = []
    confs = []

    for box in boxes_scaled:
        # Calculate confidence score
        xs, ys = box[:, 0], box[:, 1]
        min_x, max_x = max(int(np.min(xs)), 0), min(int(np.max(xs)), hmap_w)
        min_y, max_y = max(int(np.min(ys)), 0), min(int(np.max(ys)), hmap_h)

        if min_x < max_x and min_y < max_y:
            region = score_text[min_y:max_y, min_x:max_x]
            conf_val = float(np.mean(region)) if region.size > 0 else 0.0
        else:
            conf_val = 0.0
        confs.append(conf_val)

        # Normalize coordinates
        box_normalized = box.copy()
        box_normalized[:, 0] /= hmap_w
        box_normalized[:, 1] /= hmap_h
        boxes_normalized.append(box_normalized)

    return boxes_normalized, confs