import os
import yaml

def read_yaml_config(file_path):
    """
    Reads a YAML configuration file and returns it as a dictionary.


    Args: file_path (str): Path to the YAML configuration file.

    Returns:
        dict: The configuration data.
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def create_directory_with_permissions(directory, access_rights):
    """
    Checks if the directory exists. If not, creates it and sets the specified access rights.

    Args:
        directory (str): The directory path to check or create.
        access_rights (int): The access rights to set for the directory in octal format.

    Returns:
        str: Message indicating the result.
    """
    # Ensure access_rights is treated as octal
    if not isinstance(access_rights, int):
        raise ValueError("Access rights must be an integer in octal format.")

    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chmod(directory, access_rights)  # Correctly applies octal permissions
        return f"Created directory '{directory}' with permissions {oct(access_rights)}"
    else:
        # Ensure existing directory permissions match the desired permissions
        current_permissions = oct(os.stat(directory).st_mode)[-3:]
        if current_permissions != oct(access_rights)[-3:]:
            os.chmod(directory, access_rights)
            return f"Directory '{directory}' existed, updated permissions to {oct(access_rights)}"
        return f"Directory '{directory}' already exists with correct permissions."




def main():
    # Path to your YAML configuration file
    config_file = "config/config.yaml"

    # Read the YAML file into a dictionary
    config = read_yaml_config(config_file)

    # Process the 'installation' section
    installation_config = config.get("installation", {})
    root_dir = installation_config.get("root")
    access_rights = installation_config.get("accessrights")

    # Ensure access_rights is an octal integer
    if isinstance(access_rights, str):
        access_rights = int(access_rights, 8)

    # Check and create the directory
    if root_dir:
        result = create_directory_with_permissions(root_dir, access_rights)
        print(result)
    else:
        print("No root directory specified in the configuration file.")

if __name__ == "__main__":
    main()

