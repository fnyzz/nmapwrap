import os
import stat
import pwd
import grp
import logging

#@(#) ----------------------------------------------------------------
#@(@) Class name: DirManager
#@(#) input:
#@(#) return:
#@(#)        Initialize the class with a configuration dictionary and an optional logger.
#@(#)        :param config: Configuration dictionary containing directory and user info.
#@(#)        :param logger: Logger instance for logging messages.
class DirManager:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or self._setup_default_logger()

    #@(#) ----------------------------------------------------------------
    #@(@) Function:
    #@(#) input:
    #@(#) return:
    #@(#) What:
    #@(#)

    #@(#) ----------------------------------------------------------------
    #@(@) Function: _setup_default_logger
    #@(#) input: self
    #@(#) What:  Sets up a default logger if none is provided.
    #@(#) return: Configured logger instance.
    #@(#)
    def _setup_default_logger(self):
        logger = logging.getLogger("DirectoryManager")
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    #@(#) ----------------------------------------------------------------
    #@(@) Function: validate_directories
    #@(#) input: self
    #@(#) return: Returns a list of invalid directories
    #@(#) What:  Validate that the directory paths in the dictionary are valid Linux directories.
    #(@#)        Excludes directories containing spaces or non-absolute paths.
    #@(#)
    def validate_directories(self):
        self.logger.debug("Starting directory validation.")

        invalid_directories = []

        # Validate installation directories
        installation_dirs = self.config.get('installation', {})

        for key, path in installation_dirs.items():
            if ' ' in path or not os.path.isabs(path):
                self.logger.error(f"Invalid directory: {path}")
                invalid_directories.append(path)
            else:
                self.logger.debug(f"Validated installation directory: {path}")

        # Validate client directories
        client_config = self.config.get('client', {})
        client_home = client_config.get('clienthome')
        client_name = client_config.get('name')

        if client_home:
            if ' ' in client_home or not os.path.isabs(client_home):
                self.logger.error(f"Invalid client home directory: {client_home}")
                invalid_directories.append(client_home)
            else:
                self.logger.debug(f"Validated client home directory: {client_home}")

        if client_name:
            if ' ' in client_name:
                self.logger.error(f"Invalid client name: {client_name}")
                invalid_directories.append(client_name)
            else:
                self.logger.debug(f"Validated client name: {client_name}")

        self.logger.debug("Directory validation completed.")
        return invalid_directories

    #@(#) ----------------------------------------------------------------
    #@(@) Function: create_directories
    #@(#) input:    self
    #@(#) return:   Returns a list of directories that failed to be created.
    #@(#) What:     Create the directories specified in the dictionary if they don't exist.
    #@(#)
    def create_directories(self):
        self.logger.debug("Starting directory creation.")

        failed_directories = []

        # Create installation directories
        installation_dirs = self.config.get('installation', {})
        for key, path in installation_dirs.items():
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                    self.logger.info(f"Created directory: {path}")
                except Exception as e:
                    self.logger.error(f"Failed to create directory '{path}': {e}")
                    failed_directories.append(path)
            else:
                self.logger.info(f"Directory already exists: {path}")

        # Create client directories
        client_config = self.config.get('client', {})
        client_home = client_config.get('clienthome')
        client_name = client_config.get('name')

        if client_home and client_name:
            try:
                # Create the client home directory if it doesn't exist
                if not os.path.exists(client_home):
                    os.makedirs(client_home, exist_ok=True)
                    self.logger.info(f"Created client home directory: {client_home}")
                else:
                    self.logger.debug(f"Client home directory already exists: {client_home}")

                # Create the client name subdirectory
                client_name_path = os.path.join(client_home, client_name)
                if not os.path.exists(client_name_path):
                    os.makedirs(client_name_path, exist_ok=True)
                    self.logger.info(f"Created client name directory: {client_name_path}")
                else:
                    self.logger.debug(f"Client name directory already exists: {client_name_path}")
            except Exception as e:
                self.logger.error(f"Failed to create client directories: {e}")
                failed_directories.append(client_home)

        self.logger.debug("Directory creation completed.")
        return failed_directories

    #@(#) ----------------------------------------------------------------
    #@(@) Function:
    #@(#) input:
    #@(#) return:
    #@(#) What:
    #@(#)
    def set_user_and_permissions(self):
        """
        Set ownership and permissions for the directories based on the dictionary.
        Returns True if all operations are successful, otherwise False.
        """
        self.logger.debug("Starting setting user ownership and permissions.")

        uid_config = self.config.get('uid', {})
        username = uid_config.get('username')
        access_rights = uid_config.get('accessrights')

        if username is None or access_rights is None:
            self.logger.error("Username or access rights not specified in the configuration.")
            return False

        try:
            user_info = pwd.getpwnam(username)
            user_uid = user_info.pw_uid
            user_gid = user_info.pw_gid
            self.logger.debug(f"Retrieved UID: {user_uid}, GID: {user_gid} for user: {username}")
        except KeyError:
            self.logger.error(f"User '{username}' does not exist on the system.")
            return False

        # Convert access rights from string to integer (octal)
        try:
            permissions = int(access_rights, 8)
            self.logger.debug(f"Converted access rights '{access_rights}' to integer: {permissions}")
        except ValueError:
            self.logger.error(f"Invalid access rights format: '{access_rights}'. Should be octal string like '0o755'.")
            return False

        success = True


        # Set permissions for client directories
        client_config = self.config.get('client', {})
        client_home = client_config.get('clienthome')
        client_name = client_config.get('name')

        if client_home and client_name:
            client_name_path = os.path.join(client_home, client_name)
            try:
                os.chown(client_home, user_uid, user_gid)
                os.chmod(client_home, permissions)
                self.logger.info(f"Set ownership to '{username}' and permissions to '{access_rights}' for: {client_home}")

                os.chown(client_name_path, user_uid, user_gid)
                os.chmod(client_name_path, permissions)
                self.logger.info(f"Set ownership to '{username}' and permissions to '{access_rights}' for: {client_name_path}")
            except Exception as e:
                self.logger.error(f"Failed to set ownership/permissions for client directories: {e}")
                success = False

        self.logger.info("Setting user ownership and permissions completed.")
        return success

    #@(#) ----------------------------------------------------------------
    #@(@) Function: manage_directories
    #@(#) input: self
    #@(#) return: False
    #@(#) What: Perform all operations: validation, creation, and setting user/permissions.
    #@(#) Exits with False if any step fails.
    def manage_directories(self):
        self.logger.info("Managing directories started.")
        invalid_directories = self.validate_directories()
        #  + -------------------------------------------------------------
        #  + Cheking for valid directories
        if invalid_directories:
            self.logger.error(f"Invalid directories found: {invalid_directories}")
            exit(2)

        #  + -------------------------------------------------------------
        #  + Creating directories
        #  + exit if failed
        failed_directories = self.create_directories()
        if failed_directories:
            self.logger.error(f"Failed to create directories: {failed_directories}")
            exit(2)

        #  + -------------------------------------------------------------
        #  + Setting owner and permission
        #  + exit if failed
        if not self.set_user_and_permissions():
            self.logger.error(f"Failed to set access rights and owner")
            exit(False)

        self.logger.debug("Environment check completed successfully.")


