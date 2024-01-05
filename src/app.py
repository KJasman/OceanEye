from pathlib import Path
import streamlit as st
import cv2
import settings
import helper
from helper import States
from video import detect_video
from image import detect_image

state_defaults = {
    "state": States.uninitialized,
    "uploaded_media": None,
    "paths": {"original": None, "result": None, "data": None},
    "kelp_conf": 0.04,
    "model_type": 'Built-in',
    "plot_type": settings.PLOT_TYPE_OBJECTS_ONLY
}

for key in state_defaults:
    if key not in st.session_state:
        st.session_state[key] = state_defaults[key]



# Setting page layout
st.set_page_config(
    page_title="OceanEye",
    page_icon="🌊",
    layout="wide",
)
# Front Page
# Main page heading
st.header("OceanEye: Marine Detection", divider='blue')
st.subheader("Configuration")

# Main Confidence Slider
confidence = float(st.slider(
    "Select Model Confidence", 0, 100, 40,
    # on_change=helper.repredict(), 
)) / 100



# Kelp Confidence Slider (Only for Built-in)
kelp_c = st.slider(
    "Select Kelp Confidence (Image Only)", 0, 100, 10,
    # on_change=helper.repredict(),
)
st.session_state.kelp_conf = float(kelp_c) / 100

# if detect_type == "Objects Only":
model_path = Path(settings.DETECTION_MODEL)
# else:
    # model_path = Path(settings.SEGMENTATION_MODEL)
model = helper.load_model(model_path)

# Initializing Functions
if st.session_state.state == States.uninitialized:
    with st.spinner('Initializing...'):
        helper.init()
# Tabs
tab1, tab2 = st.tabs(["Detection", "About"])
# Main Detection Tab

image_extentions = ["jpg", "jpeg", "png", 'bmp', 'webp']
video_extentions = ["mp4", "mov"]


def is_image(media):
    return media.type.startswith('image')

def display_media(path, **kwargs):
    if 'use_column_width' not in kwargs:
        kwargs['use_column_width'] = True

    video_only_kwargs =  ['format', 'start_time']
    video_kwargs = {key: value for (key, value) in kwargs.items() if key in video_only_kwargs}
    image_kwargs = {key: value for (key, value) in kwargs.items() if key not in video_only_kwargs}

    with open(path, 'rb') as file:
        data = file.read()
        if Path(path).suffix[1:] in image_extentions:
            st.image(data, **image_kwargs)
        else:
            st.video(data, **video_kwargs)

def upload_media():
    with open(st.session_state.paths["original"], 'wb') as file:
        file.write(st.session_state.uploaded_media.getbuffer())
        st.session_state.state = States.file_uploaded

with tab1:
    st.session_state.uploaded_media = st.file_uploader(
            "Choose an image...",
            type=image_extentions + video_extentions,
            on_change=helper.on_upload
        )
    
    uploaded_media = st.session_state.uploaded_media

    if uploaded_media:
        left_col, right_col = st.columns(2)

        st.session_state.paths["original"] = settings.MEDIA_ORIGINAL_DIR / uploaded_media.name
        st.session_state.paths["result"] = settings.MEDIA_PROCESSED_DIR / uploaded_media.name
        st.session_state.paths["data"] = settings.MEDIA_PROCESSED_DIR / (st.session_state.paths["result"].stem + ".csv")

        if st.session_state.state == States.waiting_for_upload:
            upload_media()
        
        with left_col:
            display_media(st.session_state.paths["original"], caption="Original Image")

        with right_col:
            if st.session_state.state == States.finished_detection:
                display_media(st.session_state.paths["result"], caption="Detected Image")
                
        if st.session_state.state == States.detecting:
            if is_image(uploaded_media):
                detect_image(model, cv2.imread(str(st.session_state.paths["original"])), confidence)

            else:
                with right_col:
                    detect_video(confidence, model)

            st.session_state.state = States.finished_detection
            st.rerun()
   

    else:
        st.write("## Please Upload Media...")
        left_col, right_col = st.columns(2)
        with left_col:
            display_media(settings.DEFAULT_IMAGE, caption="Default Image")

        with right_col:
            display_media(settings.DEFAULT_DETECT_IMAGE, caption="Detected Image")

    if st.session_state.state == States.file_uploaded:
        st.button('Detect', on_click=helper.click_detect)

    if st.session_state.state == States.finished_detection:
        with open(st.session_state.paths["result"], 'rb') as file:
            # mime = "image/png" if st.session_state.uploaded_media.type.startswith("image") else "video/mp4"
            st.download_button('Download Detected File', file, file_name=f"processed_{st.session_state.uploaded_media.name}")

        with open(st.session_state.paths["data"], 'rb') as file:
            # mime = "image/png" if st.session_state.uploaded_media.type.startswith("image") else "video/mp4"
            st.download_button('Download Data', file, file_name=f"data_{st.session_state.paths['result'].stem}.csv")


with tab2:
    """
    # About the App

    Visit the GitHub for this project: https://github.com/KJasman/Spectral_Detection

    ### How to Use
    :blue[**Select Source:**] Choose to upload an image or video

    :blue[**Choose Detection Type:**] Choose to detect species only, or also use segmentation to get coverage results.

    :blue[**Select Model Confidence:**] Choose the confidence threshold cutoff for object detection. Useful for fine tuning detections on particular images.

    :blue[**Select Kelp Confidence:**] Choose the confidence threshold for the Kelp class only. This was added to allow greater detection flexibility with kelp.

    :blue[**Choose Results Formatting:**] Choose the formatting for the segmentation results. Choosing :blue[Area (Drop Quadrat)] will allow you to enter the size of the PVC surrounding the image, and the results will be in square centimeters. Choosing :blue[Percentage] will output the results as a percentage of the image area.
    
    :blue[**Choose an Image:**] Upload the images that will be used for the detection and segmentation.

    ### Image Detection
    After an image is uploaded, the :blue[**Detect**] button will display, and run the detection or segmentation based on the :blue[**Detection Type**] chosen above.
    The detected and segmented images will be displayed, along with a manual annotator and the image detection results. The Manual Annotator can be used to delete bounding boxes using :blue[del], or to add and move boxes using :blue[transform] Pressing :blue[Complete] will update the results below, and also remove any bounding boxes that were deleted from the detection and segmentation results.
    New classes can be added to the manual annotator dropdown by entering the name in the :blue[**Enter New Manual Classes**] box.
    Note: The manual annotator will not update coverage results if a new bounding box is created, or an original bounding box is resized.
    Note: The manual annotator does not support reclassifying existing bounding boxes at this time. Please delete the orignal and create a new bounding box with the new class type 

    ### Results
    A list of results will be displayed, showing the number of detections, and coverage if segmentation is selected. Coverage will be in cm^2 or %% based on the :blue[**Results Formatting**] chosen.
    Press :blue[**Download Results**] to download the csv file with the resulting data
    Press :blue[**Download Image**] to download the image files with the bounding boxes
    Press :blue[**Clear Image List**] to clear all images from the saved list
    Press :blue[**Download Data Dump**] to download the detection data in YOLO format for use with future training

    ### Batch Images
    If multiple files are uploaded, after pressing :blue[**Add To List**], pressing :blue[**Detect**] again will load the next image and start the next detection.

    ### Video Detection
    Upload a video file
    Press :blue[**Detect Video Objects**] to start the video processing (this may take a while).
    When complete, press :blue[**Detect Video Objects**] again to view the final processed video.
    Press :blue[**Add to List**] to save the video results.
    press :blue[**Download Results**] to download a csv file containing the detection statistics.
    press :blue[**Download Video**] to download the annotated video with the bounding boxes overlaid.
    press :blue[**Clear List**] to clear all video results from the list.

    ### Acknowledgements
    We would like to thank Freisen et al. for their contributions to getting this project started.
    """