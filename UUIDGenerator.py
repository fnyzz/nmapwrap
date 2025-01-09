import uuid

class UUIDGenerator:
    def __init__(self):
        """
        Initializes the UUIDGenerator instance.
        """
        pass

    def generate_uuid(self):
        """
        Generates and returns a unique UUID string.

        :return: A string representation of a UUID.
        """
        return str(uuid.uuid4())
