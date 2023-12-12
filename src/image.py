import streamlit as st
import csv
import cv2
# import numpy as np
# import supervision as sv
# from supervision.draw.color import Color
import settings


def detect_image(_model, _uploaded_image, confidence):
    # boxes = []
    # labels = []
    detections = []
    # Detection Stage
    if st.session_state.model_type == "Built-in":
        detections.append(_model.predict(_uploaded_image, conf=confidence, classes=[0,2,3], max_det=settings.MAX_DETECTION))
        detections.append(_model.predict(_uploaded_image, conf=st.session_state.kelp_conf, classes=[1], max_det=settings.MAX_DETECTION))

    else:
        detections.append(_model.predict(_uploaded_image, conf=confidence))

    use_masks = st.session_state.plot_type == settings.PLOT_TYPE_OBJECTS_AND_SEGMENTATION

    annotated_image = detections[0][0].plot(masks=use_masks)
    if len(detections) > 1:
        for result in detections[1:]:
            annotated_image = result[0].plot(img=annotated_image, masks=use_masks)

  

    results = {
        "file": st.session_state.uploaded_media.name,
        "type": st.session_state.uploaded_media.type,
        "media": f"image",
        "file_size": len(st.session_state.uploaded_media.getvalue()),
        "detections": {}
    }

    for result in detections:
        classes = result[0].names
        for box in result[0].boxes:
            box_cls = classes[box.cls.item()]
            if not results["detections"].get(box_cls):
                results["detections"][box_cls] = 0

            results["detections"][box_cls] += 1
       

    with open(st.session_state.paths["data"], "w") as f:
        writer = csv.writer(f)
        writer.writerow(['Object', 'Count'])
        
        for object, count in results["detections"].items():
            writer.writerow([object, count])
    
    cv2.imwrite(str(st.session_state.paths["result"]), cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
