from ultralytics import YOLO
import streamlit as st
import os
import os, shutil
import settings

class States:
    uninitialized = 'uninitialized'
    waiting_for_upload = 'waiting_for_upload' 
    file_uploaded = 'file_uploaded'
    detecting = 'detecting'
    finished_detection = 'finished_detection'

def load_model(model_path):
    return YOLO(model_path)

def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

def clear_folder(folder):
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

def init():
    # init_models()

    folders = [
        settings.MEDIA_DIR,
        settings.MEDIA_ORIGINAL_DIR,
        settings.MEDIA_PROCESSED_DIR,
    ]

    for folder in folders:
        create_folder(folder)
    
    #remove detected media
    clear_folder(settings.MEDIA_ORIGINAL_DIR)
    clear_folder(settings.MEDIA_PROCESSED_DIR)

    st.session_state.state = States.waiting_for_upload


# Detect Button
def click_detect():
    st.session_state.state = States.detecting

def on_upload():
    st.session_state.state = States.waiting_for_upload

