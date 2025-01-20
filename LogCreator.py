#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       LogCreator.py
#@(#) ----------------------------------------------------------------
#@(#)              $Author: Ketil $
#@(#)              Purpose: Creates a log handler for logging of events
#@(#)     Invoked by:  Ketil
#@(#) ----------------------------------------------------------------
import os
import logging
import sys
import uuid
#@(#) ----------------------------------------------------------------
#@(@) Class name: LoggerCreator
#@(#) input: a log directory, a filename, an UUID string
#@(#)        a bool value for quiet
#@(#) return: a logger handler
#@(#) What:  Initializes the the logger for logging of events.
#@(#)
class LoggerCreator:
    def __init__(self, log_directory, log_file, log_level, uuid_string, quiet=True):
        self.log_directory = log_directory
        self.log_file = log_file
        self.log_level = log_level
        self.uuid_string = uuid_string
        self.quiet = quiet

        # Ensure log directory exists
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        # Set log file path
        self.log_file_path = os.path.join(self.log_directory, self.log_file)

    #@(#) ----------------------------------------------------------------
    #@(@) Function: get_logger
    #@(#) input: reference to self and a prog.name
    #@(#) return: a logger handler
    #@(#) What:  Creates a handler for logging to a file
    #@(#)
    def get_logger(self, program_name):
        # Create logger
        logger = logging.getLogger(program_name)
        logger.setLevel(self.log_level)

        # Log format with uuid and program name
        log_format = f"%(asctime)s - %(name)s - %(levelname)s - {self.uuid_string} - %(message)s"
        formatter = logging.Formatter(log_format)

        # File handler for logging to file
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Stream handler for logging to stdout (if quiet is False)
        if not self.quiet:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger

