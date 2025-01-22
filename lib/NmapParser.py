#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       Validator.py
#@(#) ----------------------------------------------------------------
#@(#) Author: Ketil $
#@(#) Purpose: Parses the Nmap ping and writes hosts to
#@(#)          onlinehosts.client.txt who is online
#@(#)     Invoked by:  Ketil
#@(#) ----------------------------------------------------------------

import xml.etree.ElementTree as ET
#@(#) ----------------------------------------------------------------
#@(@) Class name: Validator
#@(#) input: a file
#@(#) return:
#@(#) What:  Initializes the Validator with the string to validate.
#@(#)        :param path: The string to validate as a Linux filename or path.
class NmapParser:
    def __init__(self, input_filename):
        self.input_filename = input_filename
        #print (f"input: {self.input_filename}")

    #@(#) ----------------------------------------------------------------
    #@(@) Function: is_valid
    #@(#) input: reference to self
    #@(#) return: true/false
    #@(#) What:  Validates the string as a valid Linux filename or path.
    #@(#)        :return: True if the string is valid, False otherwise.
    def get_alive_hosts(self):
        tree = ET.parse(self.input_filename)
        root = tree.getroot()
        alive_hosts = []

        for host in root.findall('host'):
            status = host.find('status').get('state')
            if status == 'up':
                address = host.find('address').get('addr')
                alive_hosts.append(address)

        return alive_hosts
    #@(#) ----------------------------------------------------------------
    #@(@) Function: is_valid
    #@(#) input: reference to self
    #@(#) return: true/false
    #@(#) What:  Validates the string as a valid Linux filename or path.
    #@(#)        :return: True if the string is valid, False otherwise.
    def write_alive_hosts_to_file(self, output_filename):
        alive_hosts = self.get_alive_hosts()
        with open(output_filename, 'w') as f:
            for host in alive_hosts:
                f.write(f"{host}\n")

# Usage example
if __name__ == "__main__":
    #input_filename = "20250113T093845_discovery_FullerLN.ping.xml"  # Replace with your actual input file name
    #output_filename = "alive_hosts.txt"  # Replace with your desired output file name
    input_filename = "/opt/nmapwrap/data/client1/20250115T183636_discovery_client1.ping.xml"
    output_filename ="/opt/nmapwrap/data/client1/onlinehosts.client1.txt"

    parser = NmapParser(input_filename)
    parser.write_alive_hosts_to_file(output_filename)

