from pathlib import Path
import os
import streamlit as st
import pandas as pd
import cv2
import numpy as np
import settings

def upload_video(source):
    source_path = Path(settings.VIDEO_ORIGINAL_DIR, source.name)
    destination_path = Path(settings.VIDEO_PROCESSED_DIR, source.name)

    bytes_data = source.getvalue()
    preview_video_upload(source_path, bytes_data)

    return source_path, destination_path


def preview_video_upload(video_name, data):
    with open(video_name, 'wb') as video_file:
        video_file.write(data)


    return video_name


def preview_finished_video(video_name):
    if os.path.exists(video_name):
        with open(video_name, 'rb') as video_file:
            video_bytes = video_file.read()
        if video_bytes:
            st.video(video_bytes)


def format_video_results(model, video_name):
    video_results = st.session_state.video_data
    st.session_state.image_name = os.path.basename(video_name)
    # Initialize empty lists to store data
    index_list = []
    class_id_list = []
    count_list = []
    select_list = []

    # [0, 132, 1, 0] {0: 'Sea Cucumber', 1: 'Sea Urchin', 2: 'Starfish', 3: 'Starfish-5'}
    for idx in range(len(video_results)):
        select = True
        index_list.append(idx + 1)
        class_id_list.append(model.names[idx])
        count_list.append(video_results[idx])
        select_list.append(select)

    data = {
        'Index': index_list,
        'class_id': class_id_list,
        'Count': count_list,
        'Select': select_list
    }
    df = pd.DataFrame(data)

    # Set class_id as the index
    df.set_index('Index', inplace=True)

    st.write("Video Tracking Results")
    edited_df = st.data_editor(df, disabled=["Index", "class_id", "Count"])

    excel = {}
    excel['Video'] = st.session_state.image_name
    for name in model.names:
        col1 = f"{model.names[name]}"
        excel[col1] = f"{video_results[name]}"

    dfex = pd.DataFrame(excel, index=[st.session_state.image_name])

    return dfex


def detect_video(conf, model):
    """
    Plays a stored video file. Tracks and detects objects in real-time using the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.
        fps: Frame rate to sample the input video at.
        source_path: Path/input.[MP4,MPEG]
        destinantion_path: Path/output.[MP4,MPEG]

    Returns:
        None

    Raises:
        None
    """
    # _, tracker = display_tracker_options()
    tracker = "bytetrack.yaml"

    try:
        vid_cap = cv2.VideoCapture(str(st.session_state.original_media_path))

        size = (int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
        fourcc = cv2.VideoWriter_fourcc('A', 'V', 'C', '1')
        video_out = cv2.VideoWriter(str(st.session_state.result_media_path), fourcc, vid_cap.get(cv2.CAP_PROP_FPS), size)

        if video_out is None:
            raise Exception("Error creating VideoWriter")

        Species_Counter = [0 for n in model.names]
        Per_Counter = [0]
        frame_count = 0

        total_frames = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))

        placeholder = st.empty()
        progress_bar = st.progress(0)


        while (vid_cap.isOpened()):
            has_frame, frame = vid_cap.read()
            if has_frame == False:
                break

            frame_count += 1

            # if frame_count % 15 != 0: continue
            progress_bar.progress(frame_count / total_frames,
                                    text=f"Processing Video Capture... ( {frame_count} / {total_frames} )")

            results = model.track(frame, conf=conf, iou=0.2, persist=True, tracker=tracker, device=settings.DEVICE,
                                    verbose=False)[0]

            if results.boxes.id is not None:

                boxes = results.boxes.xyxy.cpu().numpy().astype(int)
                ids = results.boxes.id.cpu().numpy().astype(int)
                clss = results.boxes.cls.cpu().numpy().astype(int)

                for box_num in range(len(boxes)):

                    box = boxes[box_num]
                    id = ids[box_num]
                    cls = clss[box_num]

                    # use id as first array index
                    # use class as second array index
                    # use persistance counter as third array index

                    color = (0, 255, 0)
                    while id >= len(Per_Counter) - 1:
                        Per_Counter.append(0)

                    Per_Counter[id] += 1

                    if Per_Counter[id] < 10:
                        color = (163, 0, 163)
                    elif Per_Counter[id] == 10:
                        Species_Counter[cls] += 1
                        color = (255, 0, 255)

                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
                    cv2.putText(
                        frame,
                        f"{model.names[cls].capitalize()} {round(conf, 3)}",  # Class:{cls}; Conf:{round(conf,2)} ",
                        (box[0], box[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        color,
                        2)

            x, y, w, h = 30, 40, 350, 190
            sub_img = frame[y:y + h, x:x + w]
            white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 255

            res = cv2.addWeighted(sub_img, 0.5, white_rect, 0.5, 1.0)

            # Putting the image back to its position
            frame[y:y + h, x:x + w] = res
            y = 75
            cv2.putText(frame, f"ID - NAME - COUNT", (40, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            for species in model.names.keys():
                y += 35
                cv2.putText(frame, str(species), (40, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                cv2.putText(frame, model.names[species].capitalize(), (70, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                cv2.putText(frame, str(Species_Counter[species]), (275, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            video_out.write(frame)
            placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        vid_cap.release()
        video_out.release()

        if os.path.exists(st.session_state.result_media_path):
            print("Capture Done. " + str(Species_Counter) + ' ' + str(model.names))
            st.session_state.video_data = Species_Counter
            placeholder.empty()
            return True

    except Exception as e:
        import traceback
        st.sidebar.error("Error loading video: " + str(e))
        traceback.print_exc()
    return False
