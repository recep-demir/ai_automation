import logging

# Basic configuration for the logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='app_trace.log', # Logs will be saved to this file
    filemode='a' # 'a' for append, 'w' for overwrite
)

logger = logging.getLogger("MainExplorer")

def perform_division(a, b):
    try:
        logger.info(f"Attempting to divide {a} by {b}")
        result = a / b
        return result
    except ZeroDivisionError:
        # Logging the exception with stack trace
        logger.error("Division by zero error encountered!", exc_info=True)
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}")

# Test the logger
perform_division(10, 2)
perform_division(10, 0)