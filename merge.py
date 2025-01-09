import yaml
import os

class YamlConfigReader:
    def __init__(self, file1: str, file2: str):
        self.file1 = file1
        self.file2 = file2
        self.config = {}

    def load_yaml(self, file_path):
        """Helper method to load a YAML file into a dictionary."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def merge_configs(self):
        """Load and merge the two YAML config files into one dictionary."""
        config1 = self.load_yaml(self.file1)
        config2 = self.load_yaml(self.file2)

        self.config.update(config1)  # Merge first file into the config dictionary
        self.config.update(config2)  # Merge second file into the config dictionary

        return self.config


# Example usage:
if __name__ == "__main__":
    # Replace with the paths to your YAML files
    file1 = "config/config.yaml"
    file2 = "config/TestClient.yaml"

    config_reader = YamlConfigReader(file1, file2)
    merged_config = config_reader.merge_configs()

    print("Merged Configuration:")
    for i,j in merged_config.items():
        print (f"i j {i} {j} ")
#     print(merged_config)

