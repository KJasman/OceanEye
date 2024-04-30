import os
import csv
import streamlit as st
import cv2
# import skvideo.io
import settings


def detect_video(conf, model):
    # _, tracker = display_tracker_options()
    tracker = "bytetrack.yaml"

    vid_cap = cv2.VideoCapture(str(st.session_state.paths["original"]))

    size = (int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    total_frames = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(vid_cap.get(cv2.CAP_PROP_FPS))


    mm, ss = divmod(total_frames / frame_rate, 60)
    hh, mm= divmod(mm, 60)

    results = {
        "file": st.session_state.uploaded_media.name,
        "type": st.session_state.uploaded_media.type,
        "media": f"{size[0]} x {size[1]}, {total_frames} frames, {frame_rate} fps, {int(hh):02d}:{int(mm):02d}:{int(ss):02d}",
        "file_size": len(st.session_state.uploaded_media.getvalue()),
        "detections": {}
    }
    print(str(st.session_state.paths["result"]))
    # fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
    fourcc = cv2.VideoWriter_fourcc('A', 'V', 'C', '1')
    video_out = cv2.VideoWriter(str(st.session_state.paths["result"]), fourcc, frame_rate, size)
    # video_out = skvideo.io.FFmpegWriter(str(st.session_state.paths["result"]))

    if video_out is None:
        raise Exception("Error creating VideoWriter")

    # species_counter = [0 for n in model.names]
    box_counter = {}
    frame_count = 0


    placeholder = st.empty()
    progress_bar = st.progress(0)

    while vid_cap.isOpened():
        has_frame, frame = vid_cap.read()
        if has_frame == False:
            break

        frame_count += 1

        # if frame_count % 15 != 0: continue
        progress_bar.progress(
            frame_count / total_frames,
            text=f"Processing Video Capture... ( {frame_count} / {total_frames} )"
        )

        frame_results = model.track(
            frame,
            conf=conf,
            iou=0.2,
            persist=True,
            tracker=tracker,
            device=settings.DEVICE,
            verbose=False,
        )

        use_masks = st.session_state.plot_type == settings.PLOT_TYPE_OBJECTS_AND_SEGMENTATION
        annotated_frame = frame_results[0].plot(masks=use_masks)
        rgb_annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        placeholder.image(rgb_annotated_frame)
        video_out.writeFrame(rgb_annotated_frame)
        # results["detections"].append(frame_results[0].boxes.data.tolist())

        for box in frame_results[0].boxes:
            if box.id is None:
                continue

            if not box_counter.get(box.id.item()):
                box_counter[box.id.item()] = 0

            box_counter[box.id.item()] += 1

            if box_counter[box.id.item()] == 10: #arbitrary
                classes = frame_results[0].names

                if not results["detections"].get(classes[box.cls.item()]):
                    results["detections"][classes[box.cls.item()]] = 0

                results["detections"][classes[box.cls.item()]] += 1


    vid_cap.release()
    video_out.close()

    with open(st.session_state.paths["data"], "w") as f:
        writer = csv.writer(f)
        writer.writerow(['Object', 'Count'])
        
        for object, count in results["detections"].items():
            writer.writerow([object, count])
        
        
    if os.path.exists(st.session_state.paths["result"]):
        placeholder.empty()
        return True
        

    return False
