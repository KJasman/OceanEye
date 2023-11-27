# Python In-built packages
from pathlib import Path
import PIL
import os
import numpy as np

# External packages
import streamlit as st
from ffmpy import FFmpeg

# Local Modules
import settings
import helper
from helper import States
from video import detect_video


# Stages of detection process added to session state
state_defaults = {
    "state": States.uninitialized,
    # "detect": False,
    # "predicted": False,
    # "initialized": False,
    "results": [],
    "uploaded_media": None,
    "paths": {"original": None, "result": None, "data": None},

    "video_data": [],
    "image_name": None,
    "list": None,
    "img_list": None,
    "add_to_list": False,
    "img_num": 0,
    "next_img": False,
    "segmented": False,
    "side_length": 0,
    "drop_quadrat": 'Percentage',
    "manual_class": '',
    "class_list": [],
    "kelp_conf": 0.04,
    "model_type": 'Built-in',
}

for key in state_defaults:
    if key not in st.session_state:
        st.session_state[key] = state_defaults[key]



# Setting page layout
st.set_page_config(
    page_title="OceanEye",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page heading
st.title("OceanEye: Marine Detection")

# st.sidebar.header("Image/Video Config")
# source_radio = st.sidebar.radio(
#     "Select Source", settings.SOURCES_LIST, help="Choose if a single image or video will be used for detection")

# Sidebar
st.sidebar.header("Configuration")
# Model Options
detect_type = st.sidebar.radio("Choose Detection Type", ["Objects Only", "Objects + Segmentation"])
model_type = st.sidebar.radio("Select Model", ["Built-in", "Upload"])
st.session_state.model_type = model_type

# Main Confidence Slider
confidence = float(st.sidebar.slider(
    "Select Model Confidence", 0, 100, 40,
    on_change=helper.repredict(),
)) / 100


if model_type == 'Built-in':
    # Kelp Confidence Slider (Only for Built-in)
    kelp_c = st.sidebar.slider(
        "Select Kelp Confidence", 0, 100, 10,
        on_change=helper.repredict(),
    )
    st.session_state.kelp_conf = float(kelp_c) / 100

# Selecting The Model to use
if model_type == 'Built-in':
    if detect_type == "Objects Only":
        model_path = Path(settings.DETECTION_MODEL)
    else:
        model_path = Path(settings.SEGMENTATION_MODEL)
    model = helper.load_model(model_path)

elif model_type == 'Upload':
    # Uploaded Model - Whatever you want to try out
    model_file = st.sidebar.file_uploader("Upload a model...", type=("pt"))
    if model_file:
        model_path = Path(settings.MODEL_DIR, model_file.name)
        with open(model_path, 'wb') as file:
            file.write(model_file.getbuffer())

        model = helper.load_model(model_path)

# Initializing Functions
# Put here so that the sidebars and title show up while it loads


if st.session_state.state == States.uninitialized:
    with st.spinner('Initializing...'):
        helper.init()
# Tabs
source_img = None
tab1, tab2 = st.tabs(["Detection", "About"])
# Main Detection Tab
image_extentions = ["jpg", "jpeg", "png", 'bmp', 'webp']
video_extentions = ["mp4"]


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
    st.session_state.uploaded_media = st.sidebar.file_uploader(
            "Choose an image...",
            type=image_extentions + video_extentions,
            on_change=helper.on_upload
        )
    
    uploaded_media = st.session_state.uploaded_media

    if uploaded_media:
        left_col, right_col = st.columns(2)

        st.session_state.paths["original"] = Path(settings.IMAGES_ORIGINAL_DIR if is_image(uploaded_media) else settings.VIDEO_ORIGINAL_DIR, uploaded_media.name)
        st.session_state.paths["result"] = Path(settings.IMAGES_PROCESSED_DIR if is_image(uploaded_media) else settings.VIDEO_PROCESSED_DIR, uploaded_media.name)
        st.session_state.paths["data"] = settings.VIDEO_PROCESSED_DIR / (st.session_state.paths["result"].stem + ".json")

        if st.session_state.state == States.waiting_for_upload:
            upload_media()
        
        with left_col:
            display_media(st.session_state.paths["original"], caption="Original Image")

        with right_col:
            if st.session_state.state == States.finished_detection:
                display_media(st.session_state.paths["result"], caption="Detected Image")
                
        if st.session_state.state == States.detecting:
            if is_image(uploaded_media):
                helper.predict(model, PIL.Image.open(uploaded_media), confidence, detect_type)

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
        st.sidebar.button('Detect', on_click=helper.click_detect)

    if st.session_state.state == States.finished_detection:
        with open(st.session_state.paths["result"], 'rb') as file:
            # mime = "image/png" if st.session_state.uploaded_media.type.startswith("image") else "video/mp4"
            st.download_button('Download Result', file, file_name="processed_"+st.session_state.uploaded_media.name)

        with open(st.session_state.paths["data"], 'rb') as file:
            # mime = "image/png" if st.session_state.uploaded_media.type.startswith("image") else "video/mp4"
            st.download_button('Download Data', file, file_name="data_"+st.session_state.uploaded_media.name+".json")



    # if source_radio == settings.IMAGE:
    #     # Option for Drop Quadrat selection
    #     if detect_type == "Objects + Segmentation":
    #         st.sidebar.radio("Choose Results Formatting", ["Percentage", "Area (Drop Quadrat)"], key="drop_quadrat")
    #         if st.session_state.drop_quadrat == "Area (Drop Quadrat)":
    #             st.sidebar.number_input("Side Length of Drop Quadrat (cm)", value=0, key='side_length')
    #     # Upload Image
    #     source_img_list = st.sidebar.file_uploader(
    #         "Choose an image...",
    #         type=("jpg", "jpeg", "png", 'bmp', 'webp'),
    #         key="src_img",
    #         accept_multiple_files=True)
    #     if source_img_list:
    #         try:
    #             # Save all uploaded images
    #             for img in source_img_list:
    #                 print(dict(img))
    #                 img_path = Path(settings.IMAGES_ORIGINAL_DIR, img.name)
    #                 with open(img_path, 'wb') as file:
    #                     file.write(img.getbuffer())
    #             # Update detection if necessary
    #             helper.change_image(source_img_list)
    #             # Grab the image from the list
    #             source_img = source_img_list[st.session_state.img_num]
    #         except:
    #             st.sidebar.write("There is an issue writing image files")

    #     # Default Images -- Remove in the future
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         try:
    #             if source_img is None:
    #                 default_image_path = str(settings.DEFAULT_IMAGE)
    #                 default_image = PIL.Image.open(default_image_path)
    #                 st.image(default_image_path, caption="Default Image",
    #                          use_column_width=True)
    #             else:
    #                 uploaded_image = PIL.Image.open(source_img)
    #                 if not st.session_state['detect']:
    #                     st.image(source_img, caption="Uploaded Image",
    #                              use_column_width=True)
    #         except Exception as ex:
    #             st.error("Error occurred while opening the image.")
    #             st.error(ex)
    #     with col2:
    #         if source_img is None:
    #             default_detected_image_path = str(settings.DEFAULT_DETECT_IMAGE)
    #             default_detected_image = PIL.Image.open(
    #                 default_detected_image_path)
    #             st.image(default_detected_image_path, caption='Detected Image',
    #                      use_column_width=True)
    #         else:
    #             # Uploaded image
    #             st.sidebar.button('Detect', on_click=helper.click_detect)

    #     # If Detection is clicked
    #     if st.session_state['detect'] and source_img is not None:
    #         # Perform the prediction
    #         try:
    #             helper.predict(model, uploaded_image, confidence, detect_type)
    #         except Exception as ex:
    #             Upload an image or select a model to run detection
    #             st.write(ex)
    #     # If Detection is clicked
    #     bcol1, bcol2 = st.columns(2)
    #     with bcol1:
    #         if st.session_state['detect']:
    #             # Show the detection results
    #             with st.spinner("Calculating Stats..."):
    #                 selected_df = None
    #                 try:
    #                     selected_df = helper.results_math(uploaded_image, detect_type)
    #                 except Exception as ex:
    #                     Upload an image first
    #                     # st.write(ex)

    #             # Download Button
    #             list_btn = st.button('Add to List')
    #             if list_btn and (selected_df is not None):
    #                 helper.add_to_list(selected_df, uploaded_image)
    #                 st.session_state.next_img = True
    #                 # This gets the update to be forced, removing the double detect issue.
    #                 # It does look a bit weird though, consider removing
    #                 st.experimental_rerun()
    #     with bcol2:
    #         if st.session_state['detect']:
    #             st.text_input("Enter New Manual Classes",
    #                           value="",
    #                           help="You can enter more classes here which can be used with the manual annotator. They will not be automatically detected.",
    #                           key='manual_class')

    #     # Always showing list if something is in it
    #     if st.session_state.add_to_list:
    #         Image List:
    #         st.dataframe(st.session_state.list)
    #         col1, col2, col3, col4 = st.columns(4)
    #         with col1:
    #             try:
    #                 st.download_button(label="Download Results",
    #                                    help="Download a csv with the saved image results",
    #                                    data=st.session_state.list.to_csv().encode('utf-8'),
    #                                    file_name="Detection_Results.csv",
    #                                    mime='text/csv')
    #             except:
    #                 Add items to the list to download them
    #         with col2:
    #             helper.zip_images()
    #         with col3:
    #             if st.button("Clear Image List", help="Clear the saved image data"):
    #                 helper.clear_image_list()
    #         with col4:
    #             helper.dump_data_button()


    # elif source_radio == settings.VIDEO:
    #     source_vid = st.sidebar.file_uploader("Upload a Video...", type=("mp4"), key="src_vid")
    #     if source_vid is not None:
    #         vid_path, des_path = upload_video(source_vid)

    #         if not st.session_state['detect']:
    #             success = detect_video(confidence, model, vid_path, des_path)

    #             if success:
    #                 st.session_state['detect'] = True
    #                 preview_finished_video(des_path)

    #         else:
    #             # if not os.path.exists(h264_path):
    #             #     import subprocess
    #             #     subprocess.call(args=f"ffmpeg -y -i {des_path} -c:v libx264 {h264_path}".split(" "))

    #             # video_df = helper.format_video_results(model, h264_path)
    #             # list_btn = st.button('Add to List')
    #             # if list_btn and (video_df is not None):
    #             #     helper.add_to_listv(video_df)
    #             # st.session_state.next_img = False
    #             pass

    #     else:
    #         st.session_state['detect'] = False
    #         Upload a video from the sidebar to get started.

            # if st.session_state.add_to_list:
        #     Video List:
        #     st.dataframe(st.session_state.list)
        #     col1, col2, col3 = st.columns(3)
        #     with col1:
        #         try:
        #             st.download_button( label = "Download Results",
        #                             help = "Download a csv with the saved Video results",
        #                             data=st.session_state.list.to_csv().encode('utf-8'),
        #                             file_name="Detection_Results.csv",
        #                             mime='text/csv')
        #         except:
        #             Add items to the list to download them
        #     with col2:
        #         helper.zip_video()
        #     with col3:
        #         if st.button("Clear List", help="Clear the saved data"):
        #             helper.clear_image_list()


with tab2:
    """
    # About the App

    Visit the GitHub for this project: https://github.com/KJasman/Spectral_Detection

    ### How to Use
    :blue[**Select Source:**] Choose to upload an image or video

    :blue[**Choose Detection Type:**] Choose to detect species only, or also use segmentation to get coverage results.

    :blue[**Select Model:**] Choose between the built in model, or use your own (supports .pt model files).

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
    Upload a video file in the sidebar (less than 200MB) and choose :blue[**Capture Rate**] using the slider below.
    Press :blue[**Detect Video Objects**] to start the video processing (this may take a while).
    When complete, press :blue[**Detect Video Objects**] again to view the final processed video.
    Press :blue[**Add to List**] to save the video results.
    press :blue[**Download Results**] to download a csv file containing the detection statistics.
    press :blue[**Download Video**] to download the annotated video with the bounding boxes overlaid.
    press :blue[**Clear List**] to clear all video results from the list.

    ### Acknowledgements
    We would like to thank Freisen et al. for their contributions to getting this project started.
    """