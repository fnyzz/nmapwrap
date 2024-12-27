import yaml


banner=""" \
   ___
 /'___)
| (__   ___   _   _        ____  ____
| ,__)/' _ `\( ) ( )(`\/')(_  ,)(_  ,)
| |   | ( ) || (_) | >  <  /'/_  /'/_
(_)   (_) (_)`\__, |(_/\_)(____)(____)
             ( )_| |
             `\___/'
"""

class ConfigReader:
    def __init__(self, config_file: str):
        """
        Initialize the ConfigReader with the path to a YAML configuration file.
        """
        self.config_file = config_file
        self.config_data = None

    def load_config(self):
        """
        Reads the YAML configuration file and loads its contents into a dictionary.
        """
        try:
            with open(self.config_file, 'r') as file:
                self.config_data = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")

    def get(self, key: str, default=None):
        """
        Retrieves the value for a given key from the configuration.
        Supports nested keys using dot notation (e.g., "database.host").
        """
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

# Example usage
if __name__ == "__main__":
    config_file_path = "config.yaml"

    # Example YAML file (config.yaml)
    # database:
    #   host: localhost
    #   port: 5432
    #   username: admin
    #   password: secret

    config_reader = ConfigReader(config_file_path)
    try:
        print (banner)
        config_reader.load_config()
        appname = config_reader.get("app.name")
        appver  = config_reader.get("app.version")
        appenv  = config_reader.get("app.environment")
        print (f"Application name: {appname}")
        print (f"Application version: {appver}")
        print (f"Application environemnt: {appenv}")

        approot = config_reader.get("installation.root", "/opt/nmapwrap")
        appuser = config_reader.get("installatoin.username", 'nobody')
        print(f"Installation root: {approot}")
        print(f"Installation user: {appuser}")
    except Exception as e:
        print(f"Error: {e}")

