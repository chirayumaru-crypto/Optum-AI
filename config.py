# AI Optum Configuration
# Set your OpenAI API key here or use environment variable

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
TEMPERATURE = 0.3

# Session Configuration
MAX_SESSION_DURATION = 25 * 60  # 25 minutes in seconds
FATIGUE_CHECK_INTERVAL = 60  # Check fatigue every 60 seconds
DURATION_WARNING_1 = 15 * 60  # First warning at 15 minutes
DURATION_WARNING_2 = 20 * 60  # Second warning at 20 minutes
DURATION_HALT = 25 * 60       # Halt at 25 minutes

# Clinical Configuration
DEFAULT_PATIENT_ID = "ANON"
DEBUG_MODE = False
TEST_MODE = False

# Logging Configuration
LOG_DIR = "logs"
LOG_LEVEL = "INFO"
ENABLE_AUDIT_LOG = True

# Phoropter Configuration
PHOROPTER_ENABLED = True
PHOROPTER_PORT = "COM3"  # Windows serial port (update as needed)
PHOROPTER_BAUDRATE = 115200
MAX_ADJUSTMENT_DIOPTERS = 0.50
MIN_SPHERE = -20
MAX_SPHERE = 20
MIN_CYLINDER = 0
MAX_CYLINDER = -6
MIN_AXIS = 0
MAX_AXIS = 180

# Safety Configuration
RED_FLAG_KEYWORDS = [
    "pain", "severe", "sudden", "loss", "flashing", "floaters",
    "infection", "discharge", "bleeding", "trauma", "emergency",
    "vision loss", "light sensitivity", "persistent"
]

# Quality Thresholds
PARSE_SUCCESS_THRESHOLD = 0.90
CONFIDENCE_THRESHOLD = 0.70
DEVICE_SUCCESS_THRESHOLD = 0.95

# Testing Configuration
TEST_VERBOSE = True
TEST_SHOW_DETAILS = True
