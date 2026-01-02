import logging
import os
import logger

# Get the directory where logger.py is located
# This ensures showroom.log is always created in the 'src' folder
curretn_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(curretn_dir, 'showroom.log')

# Configure the logging system
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO, # Records INFO, WARNING, ERROR, and CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8' # Support for Georgian characters in logs
)

class ShowroomLogger:
    """Class responsible for recording all system operations."""
    
    @staticmethod
    def log(message):
        """Prints message to console and writes to showroom.log file."""
        print(f"📝 [SYSTEM LOG]: {message}")
        logging.info(message)
    
    @staticmethod
    def log_error(error_msg):
        """Records errors specifically with an ERROR tag."""
        print(f"❌ [ERROR LOG]: {error_msg}")
