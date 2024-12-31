#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       progname
#@(#) ----------------------------------------------------------------
#@(#)                $Date: Wed Feb  8 20:51:21 EST 2023$
#@(#)              $Author: Ketil $
#@(#)              $Locker: koh $
#@(#)               $State: Exp $
#@(#)
#@(#)              Purpose:
#@(#)     Invoked by:  Ketil
#@(#) ----------------------------------------------------------------

import yaml

#@(#) ----------------------------------------------------------------
#@(@) Class name: ConfigReader
#@(#) input: a file
#@(#) return:
#@(#) What: Initialize the ConfigReader with the path to a YAML configuration file
#@(#)
class ConfigReader:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = None

#@(#) ----------------------------------------------------------------
#@(@) funtion name: load_config
#@(#) input: self
#@(#) return: read in the config file
#@(#) What: Reads the YAML configuration file and loads its contents into a dictionary.
#@(#)
    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.config_data = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")

#@(#) ----------------------------------------------------------------
#@(@) funtion name: get
#@(#) input: Key
#@(#) return: Value
#@(#) What: Retrieves the value for a given key from the configuration.
#@(#)      Supports nested keys using dot notation (e.g., "database.host").
#@(#)
    def get(self, key: str, default=None):
        if self.config_data is None:
            raise ValueError("Configuration data is not loaded. Call load_config() first.")

        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

