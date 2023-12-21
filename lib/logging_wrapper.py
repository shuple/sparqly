# -*- coding: utf-8 -*-

# Logging wrapper to deal with the daunting configuration

import sys
import logging

class SuppressStreamHandler(logging.StreamHandler):
    """ A custom logging handler that suppresses all stdout output """
    def emit(self, record):
        pass

def init(args={}):
    """
    Initializes and configures the logging system based on provided arguments.

    This function sets up logging to various outputs (like file and stdout), handles formatting,
    and manages the logging level. It also ensures that each type of handler (file, stdout) is unique
    and does not duplicate.

    Args:
        args (dict): Configuration options for logging
                     'log_file' specifies target log file name
                     'quiet' determines if stdout is suppressed
                     'log_level' sets the logging level like 'debug', 'info', 'warning', etc.
    """
    logger = logging.getLogger()
    logger.setLevel(log_level(args.get('log_level')))

    handlers = []
    # Log to file
    if filename := args.get('log_file', ''):
        handlers.append(logging.FileHandler(filename, mode='a'))

    # Log to stdout
    if args.get('quiet'):
        handlers.append(SuppressStreamHandler(stream=sys.stdout))
    else:
        handlers.append(logging.StreamHandler())

    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
    # Add handler
    for handler in handlers:
        # Prevent duplicate handler
        if type(handler) not in {type(existing_handler) for existing_handler in logger.handlers}:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

def log_level(log_level='info'):
    """
    Converts a log level string to its corresponding logging module level

    Args:
        log_level (str): The log level as a string (e.g., 'debug', 'info', 'warning', etc.)

    Returns:
        int: The logging level from the logging module (e.g., logging.DEBUG, logging.INFO).
             Defaults to logging.INFO if the provided level is invalid or not specified.
    """
    if log_level:
        log_level = log_level.upper()
        if hasattr(logging, log_level):
            return getattr(logging, log_level)
    return logging.INFO

def log_message(message, level='info'):
    """
    Logs a message at a specified logging level

    Args:
        message (str): The log message to be recorded.
        level (str): The logging level at which to record the message.
                     Valid options are 'debug', 'info', 'warning', 'error', and 'critical'.
                     Defaults to 'info' if not specified or if an invalid level is provided.
    """
    if hasattr(logging, level) and callable(getattr(logging, level)):
        getattr(logging, level)(message)

def create_log_function(level):
    """
    Creates and returns a logging function specific to a given log level.

    Args:
        level (str): The logging level for which to create the function.
                    Valid levels are 'debug', 'info', 'warning', 'error', and 'critical'.

    Returns:
        Function: A logging function that logs messages at the specified level.
    """
    def log_wrapper(message):
        log_message(message, level)
    return log_wrapper

# Create wrapper for logging functions
log_levels = ['debug', 'info', 'warning', 'error', 'critical']
for level in log_levels:
    globals()[level] = create_log_function(level)

if __name__ == '__main__':
    pass
