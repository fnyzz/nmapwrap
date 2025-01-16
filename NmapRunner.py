import subprocess
import sys
from time import strftime
from datetime import datetime
import time
from pathlib import Path

class NmapRunner:
    def __init__(self, client_data, nmap_path, nmap_config, sessionID, logger=None):
        """
        Initialize the NmapRunner class.

        :param client_data: dict with client information (e.g., name, logdir, IP addresses)
        :param nmap_path: Full path to the nmap program (e.g., /usr/bin/nmap)
        :param nmap_config: dict with nmap configuration options
        """
        self.client_data = client_data
        self.nmap_path = Path(nmap_path)
        self.nmap_config = nmap_config
        self.sessionID = sessionID
        self.logger = logger
        self._validate_inputs()
        #self._debug_initialization()

    def _validate_inputs(self):
        """Validate the provided inputs."""
        if not self.nmap_path.is_file():
            raise FileNotFoundError(f"Nmap executable not found at: {self.nmap_path}")

        if not isinstance(self.client_data, dict) or 'clienthome' not in self.client_data:
            raise ValueError("client_data must be a dictionary containing at least a 'clienthome' key.")

        logdir_path = Path(self.client_data['clienthome'])
        if not logdir_path.is_dir():
            raise FileNotFoundError(f"Log directory not found: {logdir_path}")

        if not isinstance(self.nmap_config, dict):
            raise ValueError("nmap_config must be a dictionary.")

    def _debug_initialization(self):
        print(f"Initialized NmapRunner with:")
        print(f"  client_data: {self.client_data}")
        print(f"  nmap_path: {self.nmap_path}")
        print(f"  nmap_config: {self.nmap_config}")

    def _build_command(self):
        """Build the nmap command using the configuration dictionary."""
        command = [str(self.nmap_path)]
        scantype = None

        for key, value in self.nmap_config.items():
            self.logger.debug(f"Key  {key} Value: {value}")
            key = str(key)
            value = str(value)
            if key == 'order':
                continue
            if key == 'genonlinehosts':
                continue
            if key == 'scanflag':
                command.append(f"{value}")
            elif key == 'scan-type':
                scantype = value
            elif key == 'ports':
                command.append(f"{value}")
            elif key == 'reports':
                command.append(f"{value} {scantype}")
            elif value:
                command.append(f"--{key} {str(value)}")
            else:
                continue

        return command, scantype

    def run(self):
        """Run the nmap command as a subprocess and log output."""
        #(#)  + ---------------------------------------------------------
        #(#)  +  housekeeping varaibles
        now = datetime.now()
        onlineFile = None
        datetoday = strftime("%Y%m%d")
        ClientName = Path(self.client_data['name'])
        logdir_path = Path(self.client_data['clienthome'])
        log_file_path = logdir_path / ClientName / f"{datetoday}.{ClientName}.log"
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            suffix = self.nmap_config.pop('suffix')
        except Exception as e:
            if self.logger:
                self.logger.error(f"Fail in parsing filename suffix: {e}")
            else:
                print(f"Fail in parsing filename suffix : {e}")

        #(#) +  ------------------------------------------------------
        #(#) +  building the Nmap command from the input dict.
        command, scantype = self._build_command()

        #(#) +  ------------------------------------------------------
        #(#) +  building the report file
        #(#) +
        NmapReportName = f"{self.sessionID}_{scantype}_{ClientName}"
        FullPathReport = str(logdir_path) + "/" +  str(ClientName)  + "/" + NmapReportName + "." + suffix
        onlineFile = logdir_path / ClientName / f"onlinehosts.{ClientName}.txt"


        #(#) +  ------------------------------------------------------
        #(#) +  If the genonlinehosts is set, then we use the IP from the
        #(#) +  client config. You may use genonlinehosts in all section, but
        #(#) +  the point is to have the ping find host online to speed up
        #(#) +  the next steps.
        #(#) +  if this is not set, then we read IP from file -iL
        #(#) +
        target_ips = self.client_data.get("clientip", [])
        if self.nmap_config.get('genonlinehosts'):
            if not target_ips:
                raise ValueError("No target IP addresses provided in client_data.")
            command.append(target_ips)
        else:
            #(#) + Building the nmap -iL <onlinehosts.txt>
            #(#) + Adding this to the nmap command
            target_ips = "-iL  " + str(onlineFile)
            command.append(target_ips)

        #(#) +  ------------------------------------------------------
        #(#) +  Replacing the 'scan-type' in the command with the correct
        #(#) +  Nmap output filename.
        #(#) +  Converting from List object to String.
        #(#) +
        command = [item.replace(scantype, FullPathReport) if scantype in item else item for item in command]
        command = " ".join(command)

        if self.logger:
            self.logger.debug(f"Nmap {scantype} command to run: {command}")

        #(#) +  ------------------------------------------------------
        #(#) +  using Python subprocess to run the nmap command
        #(#) +  shell=true is not the best option for secuirty, but this program
        #(#) +  need to run as root ( nmap -sS needs root access).
        #(#) +  The output to the console is frozen and output is sent to the dailylogfile
        #(#) +  where you can monitor the output from the nmap command.
        #(#) +
        try:
            with open(log_file_path, "a") as dailylogfile:
                process = subprocess.Popen(
                    [command],
                    stdout=dailylogfile,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                stdout, stderr = process.communicate()
                if process.returncode != 0:
                    raise RuntimeError(f"Nmap command failed: {stderr}")

                if self.logger:
                    self.logger.info(f"Nmap completed successfully: {stdout}")
                else:
                    print(f"Nmap completed successfully: {stdout}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error running nmap: {e}")
            else:
                print(f"Error running nmap: {e}")
        print (f"onlineFile {onlineFile}")
        print (f"FullPathReport {FullPathReport}")

        return onlineFile, FullPathReport

# Example Usage:
# client_data = {
#     "name": "Client1",
#     "clienthome": "/path/to/logs",
#     "clientip": ["192.168.1.1", "192.168.1.2"]
# }
# nmap_path = "/usr/bin/nmap"
# nmap_config = {
#     "sS": None,  # Syn scan
#     "p": "80,443",  # Ports
#     "oN": "-"  # Normal output
# }
# runner = NmapRunner(client_data, nmap_path, nmap_config)
# runner.run()
