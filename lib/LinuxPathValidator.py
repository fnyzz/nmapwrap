import os
import re

class LinuxPathValidator:
    def __init__(self, path: str):
        """
        Initializes the LinuxPathValidator with the string to validate.
        :param path: The string to validate as a Linux filename or path.
        """
        self.path = path

    def is_valid(self) -> bool:
        """
        Validates the string as a valid Linux filename or path.
        :return: True if the string is valid, False otherwise.
        """
        # Ensure the string is not empty
        if not self.path:
            return False

        # Ensure the string does not contain invalid characters, including spaces
        # Invalid characters for filenames in Linux are null character, '/', and space
        invalid_chars = re.compile(r'[<>:"|?*\0 ]')  # Added space to the pattern
        if invalid_chars.search(self.path):
            return False

        # Ensure no component of the path is longer than 255 characters
        components = self.path.split('/')
        if any(len(comp) > 255 for comp in components if comp):  # Ignore empty parts from multiple slashes
            return False

        # Check the overall path length does not exceed 4096 characters
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
        validator = LinuxPathValidator(path)
        result = validator.is_valid()
        print(f"'{path}' -> {result}")

