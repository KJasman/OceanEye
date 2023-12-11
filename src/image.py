import streamlit as st
import csv
import cv2
import numpy as np
import supervision as sv
from supervision.draw.color import Color
import settings

def detect_image(_model, _uploaded_image, confidence):
    boxes = []
    labels = []
    # Detection Stage
    if st.session_state.model_type == "Built-in":
        non_kelp_result = _model.predict(_uploaded_image, conf=confidence, classes = [0,2,3], max_det=settings.MAX_DETECTION)
        kelp_result = _model.predict(_uploaded_image, conf=st.session_state.kelp_conf, classes = [1], max_det=settings.MAX_DETECTION)

        classes = non_kelp_result[0].names
        non_kelp_detection = sv.Detections.from_yolov8(non_kelp_result[0])
        kelp_detections = sv.Detections.from_yolov8(kelp_result[0])
        detections = sv.Detections.merge([kelp_detections, non_kelp_detection])

        if non_kelp_detection.mask is None:
            detections.mask = kelp_detections.mask
        elif kelp_detections.mask is None:
            detections.mask = non_kelp_detection.mask
        # boxes = detections.xyxy
    else:
        result = _model.predict(_uploaded_image, conf=confidence)
        classes = result[0].names
        detections = sv.Detections.from_yolov8(result[0])
        # boxes = detections.xyxy

    if(detections is not None):
        labels = [
            f"{idx} {classes[class_id]} {confidence:0.2f}"
            for idx, [_, _, confidence, class_id, _] in enumerate(detections)
            ]

    box_annotator = sv.BoxAnnotator(text_scale=2, text_thickness=3, thickness=3, text_color=Color.white())
    annotated_image = box_annotator.annotate(scene=np.array(_uploaded_image), detections=detections, labels=labels)

    results = {
        "file": st.session_state.uploaded_media.name,
        "type": st.session_state.uploaded_media.type,
        "media": f"image",
        "file_size": len(st.session_state.uploaded_media.getvalue()),
        "detections": {}
    }

    for detection in detections.class_id:
        if not results["detections"].get(classes[detection]):
            results["detections"][classes[detection]] = 0

        results["detections"][classes[detection]] += 1


    with open(st.session_state.paths["data"], "w") as f:
        writer = csv.writer(f)
        writer.writerow(['Object', 'Count'])
        
        for object, count in results["detections"].items():
            writer.writerow([object, count])
    
    cv2.imwrite(str(st.session_state.paths["result"]), cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
