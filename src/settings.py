from pathlib import Path
import sys
import cv2

# Get the absolute path of the current file
file_path = Path(__file__).resolve()

# Get the parent directory of the current file
root_path = file_path.parent

# Add the root path to the sys.path list if it is not already there
if root_path not in sys.path:
    sys.path.append(str(root_path))

# Get the relative path of the root directory with respect to the current working directory
ROOT = root_path.relative_to(Path.cwd())

# DEvice
DEVICE = "cuda" if cv2.cuda.getCudaEnabledDeviceCount() else "cpu"

# Sources
IMAGE = 'Image'
VIDEO = 'Video'

SOURCES_LIST = [IMAGE, VIDEO]

MEDIA_DIR = ROOT / 'media'
MEDIA_ORIGINAL_DIR = MEDIA_DIR / 'original'
MEDIA_PROCESSED_DIR = MEDIA_DIR / 'processed'

DEFAULT_DIR = ROOT / 'default'
DEFAULT_IMAGE = DEFAULT_DIR / 'original.jpg'
DEFAULT_DETECT_IMAGE = DEFAULT_DIR / 'processed.jpg'


# ML Model config
MODEL_DIR = ROOT / 'weights'
DETECTION_MODEL = MODEL_DIR / 'new_model.pt'
# DETECTION_MODEL = MODEL_DIR / 'SLseg_Vn.pt'
# SEGMENTATION_MODEL = MODEL_DIR / 'SLseg_Vn.pt'
SEGMENTATION_MODEL = DETECTION_MODEL
DATA_DIR = ROOT / 'Dump'

#Colors
RED = (0,0,255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
COLOR_LIST = (RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, WHITE)

#Web App breaks with a lot of detections, so it is limited here
MAX_DETECTION = 30

PLOT_TYPE_OBJECTS_ONLY = "Objects"
PLOT_TYPE_OBJECTS_AND_SEGMENTATION = "Objects + Segmentation"
