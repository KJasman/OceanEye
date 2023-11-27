from pathlib import Path
import os
import streamlit as st
import pandas as pd
import cv2
import numpy as np
import settings
import json

# def format_video_results(model, video_name):
#     video_results = st.session_state.video_data
#     st.session_state.image_name = os.path.basename(video_name)
#     # Initialize empty lists to store data
#     index_list = []
#     class_id_list = []
#     count_list = []
#     select_list = []

#     # [0, 132, 1, 0] {0: 'Sea Cucumber', 1: 'Sea Urchin', 2: 'Starfish', 3: 'Starfish-5'}
#     for idx in range(len(video_results)):
#         select = True
#         index_list.append(idx + 1)
#         class_id_list.append(model.names[idx])
#         count_list.append(video_results[idx])
#         select_list.append(select)

#     data = {
#         'Index': index_list,
#         'class_id': class_id_list,
#         'Count': count_list,
#         'Select': select_list
#     }
#     df = pd.DataFrame(data)

#     # Set class_id as the index
#     df.set_index('Index', inplace=True)

#     st.write("Video Tracking Results")
#     edited_df = st.data_editor(df, disabled=["Index", "class_id", "Count"])

#     excel = {}
#     excel['Video'] = st.session_state.image_name
#     for name in model.names:
#         col1 = f"{model.names[name]}"
#         excel[col1] = f"{video_results[name]}"

#     dfex = pd.DataFrame(excel, index=[st.session_state.image_name])

#     return dfex


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

    # fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
    fourcc = cv2.VideoWriter_fourcc('A', 'V', 'C', '1')
    video_out = cv2.VideoWriter(str(st.session_state.paths["result"]), fourcc, frame_rate, size)

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

        annotated_frame = frame_results[0].plot()
        placeholder.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
        video_out.write(annotated_frame)
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


        # print()
        # if frame_results[0].boxes.id is not None:

        #     boxes = results.boxes.xyxy.cpu().numpy().astype(int)
        #     ids = results.boxes.id.cpu().numpy().astype(int)
        #     clss = results.boxes.cls.cpu().numpy().astype(int)

            # print(boxes)

        #     for box_num in range(len(boxes)):

        #         box = boxes[box_num]
        #         id = ids[box_num]
        #         cls = clss[box_num]

        #         # use id as first array index
        #         # use class as second array index
        #         # use persistance counter as third array index

        #         color = (0, 255, 0)
        #         while id >= len(per_counter) - 1:
        #             per_counter.append(0)

        #         per_counter[id] += 1

        #         if per_counter[id] < 10:
        #             color = (163, 0, 163)
        #         elif per_counter[id] == 10:
        #             species_counter[cls] += 1
        #             color = (255, 0, 255)

        #         cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
        #         cv2.putText(
        #             frame,
        #             f"{model.names[cls].capitalize()} {round(conf, 3)}",  # Class:{cls}; Conf:{round(conf,2)} ",
        #             (box[0], box[1] - 20),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             2,
        #             color,
        #             2)

        # x, y, w, h = 30, 40, 350, 190
        # sub_img = frame[y:y + h, x:x + w]
        # white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 255

        # res = cv2.addWeighted(sub_img, 0.5, white_rect, 0.5, 1.0)

        # # Putting the image back to its position
        # frame[y:y + h, x:x + w] = res
        # y = 75
        # cv2.putText(frame, f"ID - NAME - COUNT", (40, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # for species in model.names.keys():
        #     y += 35
        #     cv2.putText(frame, str(species), (40, y),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        #     cv2.putText(frame, model.names[species].capitalize(), (70, y),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        #     cv2.putText(frame, str(species_counter[species]), (275, y),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        # video_out.write(frame)
        # placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    vid_cap.release()
    video_out.release()

    with open(st.session_state.paths["data"], "w") as f:
        json.dump(results, f)

    if os.path.exists(st.session_state.paths["result"]):
        # st.session_state.video_data = species_counter
        placeholder.empty()
        return True
        

    return False
