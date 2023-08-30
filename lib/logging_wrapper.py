# -*- coding: utf-8 -*-

import sys
import logging

# custom handler to suppress stdout
#
class SuppressStreamHandler(logging.StreamHandler):
    def emit(self, record):
        pass

# initialize logging
#
# args['log_file']  : target log file name
# args['quiet']     : suppress stdout
# args['log_level'] : 'debug', 'info', 'warning', 'error', 'critical'
#
def init(args={}):
    logger = logging.getLogger()
    logger.setLevel(log_level(args.get('log_level')))

    handlers = []
    # log to file
    if filename := args.get('log_file', ''):
        handlers.append(logging.FileHandler(filename, mode='a'))

    # log to stdout
    if args.get('quiet'):
        handlers.append(SuppressStreamHandler(stream=sys.stdout))
    else:
        handlers.append(logging.StreamHandler())

    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
    # add handler
    for handler in handlers:
        # prevent duplicate handler
        if type(handler) not in {type(existing_handler) for existing_handler in logger.handlers}:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

# return logging.level
#
# level : 'debug', 'info', 'warning', 'error', 'critical'
#
def log_level(log_level='info'):
    if log_level:
        log_level = log_level.upper()
        if hasattr(logging, log_level):
            return getattr(logging, log_level)
    return logging.INFO

# wrapper of logging.debug, logging.info, logging.warning, logging.error, logging.critical
#
# message : log message
# level   : 'debug', 'info', 'warning', 'error', 'critical'
#
def log_message(message, level='info'):
    if hasattr(logging, level) and callable(getattr(logging, level)):
        getattr(logging, level)(message)

# create debug, info, warning, error, critical methods
#
# level   : 'debug', 'info', 'warning', 'error', 'critical'
# message : log message
#
def create_log_function(level):
    def log_wrapper(message):
        log_message(message, level)
    return log_wrapper

log_levels = ['debug', 'info', 'warning', 'error', 'critical']
for level in log_levels:
    globals()[level] = create_log_function(level)

if __name__ == '__main__':
    pass
