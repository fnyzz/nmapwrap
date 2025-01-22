#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       UUIDGenerator.py
#@(#) ----------------------------------------------------------------
#@(#) Author: Ketil $
#@(#) Purpose: Generate an UUID for unique id for each scan
#@(#) Invoked by:  Ketil
#@(#) ----------------------------------------------------------------


import uuid
#@(#) ----------------------------------------------------------------
#@(@) Class name: UUIDGenerator
#@(#) input:
#@(#) return: an UUID string
#@(@) What:  Initializes the UUIDGenerator instance.
#@(#)
class UUIDGenerator:
    def __init__(self):
        pass
    #@(#) ----------------------------------------------------------------
    #@(@) Function: generate_uuid
    #@(#) input: reference to self
    #@(#) return: a UUID string
    #@(#) What:  generates the UUID string
    #@(#)
    def generate_uuid(self):
        """
        Generates and returns a unique UUID string.

        :return: A string representation of a UUID.
        """
        return str(uuid.uuid4())
