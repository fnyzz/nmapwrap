#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       nmapwrap
#@(#) ----------------------------------------------------------------
#@(#) Purpose:  Read the README.md file for details.
#@(#) Author :  Ketil
#@(#) year   :  2025
#@(#)
#@(#) ----------------------------------------------------------------

import yaml
import os

#@(#) ----------------------------------------------------------------
#@(@) Class name: ConfigReader
#@(#) input: two files on yaml format
#@(#) return:
#@(#)        Initialize the class with two yaml files
#@(#)        :param config:
#@(#)        :param logger: Logger instance for logging messages.
class ConfigReader:
    def __init__(self, file1: str, file2: str):
        self.file1 = file1
        self.file2 = file2
        self.config = {}

    #@(#) ----------------------------------------------------------------
    #@(@) Function: load_yaml
    #@(#) input:    a fil on yaml format
    #@(#) return:   a yaml object
    #@(#) What:     Reads the yyaml file, pupulates the yaml object.
    #@(#)
    def load_yaml(self, file_path):
        """Helper method to load a YAML file into a dictionary."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    #@(#) ----------------------------------------------------------------
    #@(@) Function: merge_configs
    #@(#) input:    a reference to self
    #@(#) return:   an object of merged content from 2 yaml files.
    #@(#) What:
    #@(#)
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
    file1 = "config1.yaml"
    file2 = "config2.yaml"

    config_reader = ConfigReader(file1, file2)
    merged_config = config_reader.merge_configs()

    print("Merged Configuration:")
    print(merged_config)

