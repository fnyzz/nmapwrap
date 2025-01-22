#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       SetPermission
#@(#) ----------------------------------------------------------------
#@(#) Purpose:  Validate user, set the permission
#@(#) Author :  Ketil
#@(#) year   :  2025
#@(#)
#@(#) ----------------------------------------------------------------
import os
import pwd
import logging

#@(#) ----------------------------------------------------------------
#@(@) Class: SetPersmission
#@(#) input: self
#@(#) return: False
#@(#) What: Initialize the PermissionManager class.
#@(#)         :param config: Dictionary containing 'username' and 'accessrights'.
#@(#)         :param directory: Directory on which to set permissions.
#@(#)         :param logger: Logger instance for logging messages.
class SetPermission:
    def __init__(self, config, directory, logger=None):
        self.config = config
        self.directory = directory
        self.logger = logger or self._setup_default_logger()
    #@(#) ----------------------------------------------------------------
    #@(@) Function: _setup_default_logger
    #@(#) input: self
    #@(#) return: Configured logger instance.
    #@(#) What: Set up a default logger if none is provided.
    def _setup_default_logger(self):
        logger = logging.getLogger("PermissionManager")
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    #@(#) ----------------------------------------------------------------
    #@(@) Function: validate_user
    #@(#) input: self
    #@(#) return: true/false
    #@(#) What: Validate that the username exists on the Linux system.
    def validate_user(self):
        username = self.config.get('username')
        if not username:
            self.logger.error("Username is not specified in the configuration.")
            return False

        try:
            pwd.getpwnam(username)
            self.logger.info(f"Username '{username}' is valid.")
            return True
        except KeyError:
            self.logger.error(f"Username '{username}' does not exist on the system.")
            return False

    #@(#) ----------------------------------------------------------------
    #@(@) Function: convert_access_rights
    #@(#) input: self
    #@(#) return: Integer representation of access rights, or None if invalid.
    #@(#) What: Convert access rights from string to integer (octal).
    def convert_access_rights(self):
        access_rights = self.config.get('accessrights')
        if not access_rights:
            self.logger.error("Access rights are not specified in the configuration.")
            return None

        try:
            permissions = int(access_rights, 8)
            self.logger.info(f"Access rights '{access_rights}' converted to integer: {permissions}")
            return permissions
        except ValueError:
            self.logger.error(f"Invalid access rights format: '{access_rights}'. Must be an octal string like '0o755'.")
            return None

    #@(#) ----------------------------------------------------------------
    #@(@) Function:set_permissions
    #@(#) input: self
    #@(#) return: True/False
    #@(#) What: Recursively set ownership and permissions on the given directory.
    def set_permissions(self):
        username = self.config.get('username')
        permissions = self.convert_access_rights()

        if not self.validate_user() or permissions is None:
            return False

        try:
            user_info = pwd.getpwnam(username)
            user_uid = user_info.pw_uid
            user_gid = user_info.pw_gid
        except KeyError:
            self.logger.error(f"Failed to retrieve user information for '{username}'.")
            return False

        success = True

        for root, dirs, files in os.walk(self.directory):
            for name in dirs + files:
                path = os.path.join(root, name)
                try:
                    os.chown(path, user_uid, user_gid)
                    os.chmod(path, permissions)
                    # self.logger.info(f"Set ownership to '{username}' and permissions to '{permissions:o}' for: {path}")
                except Exception as e:
                    self.logger.error(f"Failed to set permissions for '{path}': {e}")
                    success = False

        # self.logger.info(f"Permissions set successfully for directory: {self.directory}")
        return success

# Example Usage:
if __name__ == "__main__":
    config = {
        'username': 'myuser',
        'accessrights': '0o755'
    }
    directory = '/opt/nmapwrap/data/TestDate'

    # Set up logging
    logger = logging.getLogger("PermissionManagerExample")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Create and use PermissionManager
    manager = SetPermission(config, directory, logger)
    if manager.set_permissions():
        logger.info("Permissions successfully applied.")
    else:
        logger.error("Failed to apply permissions.")

