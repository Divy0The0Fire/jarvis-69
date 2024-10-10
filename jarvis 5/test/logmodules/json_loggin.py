import logging
import json
from pythonjsonlogger import jsonlogger

# Create a logger
logger = logging.getLogger('jsonLogger')
logger.setLevel(logging.DEBUG)

# Create a handler that writes log messages to a file
logHandler = logging.FileHandler('app.json')

# Set the formatter to use JSON
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
logHandler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(logHandler)

# Example usage
logger.info('This is an info message', extra={'user_id': 123, 'action': 'login'})
logger.error('This is an error message', extra={'user_id': 123, 'error': 'Invalid password'})
