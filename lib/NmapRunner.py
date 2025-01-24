#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       NmapRunner
#@(#) ----------------------------------------------------------------
#@(#) Purpose:  Run the nmap command in a sub process
#@(#)           Nmap command is build from the dict
#@(#) Author :  Ketil
#@(#) year   :  2025
#@(#)
#@(#) ----------------------------------------------------------------
import subprocess
import sys
import re
from time import strftime
from datetime import datetime
import time
from pathlib import Path

#@(#) ----------------------------------------------------------------
#@(@) Class name: NmapRunner
#@(#) input: a dict, a full path to Nmap, a dict for nmap config, a UUID, a logger
#@(#) return: self
#@(#)        Initialize the class with a configuration dictionary and an optional logger.
#@(#)         client_data: dict with client information (e.g., name, logdir, IP addresses)
#@(#)         nmap_path: Full path to the nmap program (e.g., /usr/bin/nmap)
#@(#)         nmap_config: dict with nmap configuration options
#@(#)
class NmapRunner:
    def __init__(self, client_data, nmap_path, nmap_config, sessionID, logger=None):

        self.client_data = client_data
        self.nmap_path = Path(nmap_path)
        self.nmap_config = nmap_config
        self.sessionID = sessionID
        self.logger = logger
        self._validate_inputs()
        #self._debug_initialization()

    #@(#) ----------------------------------------------------------------
    #@(@) Function: _validate_inpits
    #@(#) input: self
    #@(#) What:  input validation ( a start )
    #@(#) return: Configured logger instance.
    #@(#)
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

    #@(#) ----------------------------------------------------------------
    #@(@) Function: _debug_initialization
    #@(#) input: self
    #@(#) What:  Print input if debug
    #@(#) return: none
    #@(#)
    def _debug_initialization(self):
        self.logger.debug(f"Initialized NmapRunner with:")
        self.logger.debug(f"  client_data: {self.client_data}")
        self.logger.debug(f"  nmap_path: {self.nmap_path}")
        self.logger.debug(f"  nmap_config: {self.nmap_config}")

    #@(#) ----------------------------------------------------------------
    #@(@) Function: _replace_in_list
    #@(#) input: self
    #@(#) What:  Replace the -oA|-oN|-oX|-oS|-oG <scantype>
    #@(#)        with new_reportstring
    #@(#) return: a string: new command line
    #@(#)
    def _replace_in_list(self,lst,new_reportstring):
        pattern = r"\s*(-oA|-oN|-oX|-oS|-oG)\s+(.+)"

        for i, element in enumerate(lst):
            match = re.match(pattern, element)
            if match:
                # Preserve leading spaces, replace the old string (group 2) with new_string
                leading_spaces = element[:match.start(1)]  # Capture leading spaces
                prefix = match.group(1)  # Capture the prefix (e.g., -oA)
                lst[i] = f"{leading_spaces}{prefix} {new_reportstring}"
        return lst


    #@(#) ----------------------------------------------------------------
    #@(@) Function: _build_command
    #@(#) input: self
    #@(#) What:  Building the nmap command.
    #@(#) return: a string of Nmap options, a string of scan-type
    #@(#)
    def _build_command(self):
        """Build the nmap command using the configuration dictionary."""
        command = [str(self.nmap_path)]
        scantype = None

        for key, value in self.nmap_config.items():
            # self.logger.debug(f"Key  {key} Value: {value}")
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

    #@(#) ----------------------------------------------------------------
    #@(@) Function: run
    #@(#) input: self
    #@(#) What:  Runs the nmap command with the command line option
    #@(#) return:2 files, online filename and nmap result filename
    #@(#)
    def run(self):
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
        #(#) +  Conflickt
        command = self._replace_in_list(command, FullPathReport)
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
        self.logger.debug (f"onlineFile {onlineFile}")
        self.logger.debug (f"FullPathReport {FullPathReport}")

        return onlineFile, FullPathReport


# Example usage
if __name__ == "__main__":
    print (f"cannot run by it selves! ")
