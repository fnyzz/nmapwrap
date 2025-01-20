#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       Validator.py
#@(#) ----------------------------------------------------------------
#@(#)              $Author: Ketil $
#@(#)              Purpose:
#@(#)     Invoked by:  Ketil
#@(#) ----------------------------------------------------------------

import os
import re

#@(#) ----------------------------------------------------------------
#@(@) Class name: Validator
#@(#) input: a file
#@(#) return:
#@(#) What:  Initializes the Validator with the string to validate.
#@(#)        :param path: The string to validate as a Linux filename or path.
class Validator:
    #@(#)
    def __init__(self, path: str):
        self.path = path

    #@(#) ----------------------------------------------------------------
    #@(@) Function: is_valid
    #@(#) input: reference to self
    #@(#) return: true/false
    #@(#) What:  Validates the string as a valid Linux filename or path.
    #@(#)        :return: True if the string is valid, False otherwise.
    def is_valid_filedir(self) -> bool:
        #  +  -----------------------------------------------------------
        #  +  Make sure the string is not empty
        if not self.path:
            return False

        #  +  -----------------------------------------------------------
        #  +  Checking if the string contain invalid characters, including spaces
        #  +  Invalid characters for filenames in Linux are null character, '/', and space
        invalid_chars = re.compile(r'[<>:"|?*\0 ]')  # Added space to the pattern
        if invalid_chars.search(self.path):
            return False

        #  +  -----------------------------------------------------------
        #  +  Checking if any element of the path is longer than 255 characters
        components = self.path.split('/')
        if any(len(comp) > 255 for comp in components if comp):  # Ignore empty parts from multiple slashes
            return False

        #  +  -----------------------------------------------------------
        #  +  Check the overall path length does not exceed 4096 characters
        if len(self.path) > 4096:
            return False

        return True



# Example usage
if __name__ == "__main__":
    test_paths = [
        "valid-filename.txt",
        "/home/user/docs/valid-filename.txt",
        "/home/user/invalid<>file",
        "/home/user/valid-folder/",
        "invalid filename with space.txt",
        "/home/user/invalid /file",
        "",
        "a" * 300,  # Too long component
        "/home/user/" + "a" * 300,  # Valid component too long
    ]
    for path in test_paths:
        validator = Validator(path)
        result = validator.is_valid_filedir()
        print(f"'{path}' -> {result}")

