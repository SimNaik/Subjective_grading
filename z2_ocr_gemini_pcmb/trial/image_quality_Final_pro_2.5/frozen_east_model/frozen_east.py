import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

def east_text_detect_with_angle(image, east_model_path, min_confidence=0.5, width=320, height=320):
    # Resize image to multiples of 32
    orig = image.copy()
    (origH, origW) = image.shape[:2]
    rW = origW / float(width)
    rH = origH / float(height)
    image = cv2.resize(image, (width, height))

    # Prepare input blob
    blob = cv2.dnn.blobFromImage(image, 1.0, (width, height),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net = cv2.dnn.readNet(east_model_path)
    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"
    ]
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    # Decode predictions and extract rotated rectangles, confidence and angles
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
    angles = []
    for y in range(numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        for x in range(numCols):
            if scoresData[x] < min_confidence:
                continue
            # Geometry and box calculations
            offsetX, offsetY = x * 4.0, y * 4.0
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # Rotated box calculation
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(float(scoresData[x]))
            angles.append(float(angle))

    # Non-max suppression to refine boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # Prepare output: [(x1, y1, x2, y2, confidence, angle)]
    output = []
    for i, (startX, startY, endX, endY) in enumerate(boxes):
        # Scale box coordinates back to original image size
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        conf = confidences[i] if i < len(confidences) else None
        ang = angles[i] if i < len(angles) else None
        output.append((startX, startY, endX, endY, conf, ang))
    return output