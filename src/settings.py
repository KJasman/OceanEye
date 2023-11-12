from pathlib import Path
import sys
import torch

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
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Sources
IMAGE = 'Image'
VIDEO = 'Video'

SOURCES_LIST = [IMAGE, VIDEO]

MEDIA_DIR = ROOT / 'media'

IMAGES_DIR = MEDIA_DIR / 'images'
IMAGES_ORIGINAL_DIR = IMAGES_DIR / 'original'
IMAGES_PROCESSED_DIR = IMAGES_DIR / 'processed'

VIDEO_DIR = MEDIA_DIR / 'videos'
VIDEO_ORIGINAL_DIR = VIDEO_DIR / 'original'
VIDEO_PROCESSED_DIR = VIDEO_DIR / 'processed'

DEFAULT_DIR = ROOT / 'default'
DEFAULT_IMAGE = DEFAULT_DIR / 'original.jpg'
DEFAULT_DETECT_IMAGE = DEFAULT_DIR / 'processed.jpg'


# ML Model config
MODEL_DIR = ROOT / 'weights'
DETECTION_MODEL = MODEL_DIR / 'SLseg_Vn.pt'
# DETECTION_MODEL = MODEL_DIR / 'jun26_urchin_seastar_cucumber.pt'
SEGMENTATION_MODEL = MODEL_DIR / 'SLseg_Vn.pt'
# SEGMENTATION_MODEL = DETECTION_MODEL
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