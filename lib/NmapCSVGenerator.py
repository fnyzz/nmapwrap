#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       NmapCSVGenerator.py
#@(#) ----------------------------------------------------------------
#@(#) Author: Ketil $
#@(#) Purpose: Generates CSV file from NMAP xml files.
#@(#) Invoked by:  Ketil
#@(#) ----------------------------------------------------------------

import csv
from netaddr import IPAddress
from libnmap.parser import NmapParser

#@(#) ----------------------------------------------------------------
#@(@) Class name: NmapCSVGenerator
#@(#) input: a nmap file on XML format
#@(#) return: a file on csv format
#@(#) What:  Reads two files, a ping xml file and a tcp xml file.
#@(#)
class NmapCSVGenerator:
    def __init__(self, xmllist,logger=None):
        self.xmllist = xmllist
        self.ping_file = None
        self.tcp_files = []
        self._separate_files()
        self.logger = logger or self._setup_default_logger()


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

    #@(#) ----------------------------------------------------------------
    #@(@) Function: _separate_files
    #@(#) input: reference to self
    #@(#) return: populates the ping_file and tcp_files variable
    #@(#) What:  You can add 1 ping.xml file and multiple tcp.xml files
    #@(#)        and this function will seperate them into two seperate
    #@(#)        variables.
    #@(#)
    def _separate_files(self):
        for file in self.xmllist:
            if file.endswith("ping.xml"):
                self.ping_file = file
            elif file.endswith("tcp.xml"):
                self.tcp_files.append(file)


    #@(#) ----------------------------------------------------------------
    #@(@) Function: _combine_tcp_files
    #@(#) input: reference to self
    #@(#) return: object containing all data from all tcp.xml files
    #@(#) What:
    #@(#)
    def _combine_tcp_files(self):
        combined_hosts = []
        for tcp_file in self.tcp_files:
            parsed_data = NmapParser.parse_fromfile(tcp_file)
            combined_hosts.extend(parsed_data.hosts)
        return combined_hosts

    #@(#) ----------------------------------------------------------------
    #@(@) Function: generate_csv
    #@(#) input: reference to self
    #@(#) return: writes to the output_filename
    #@(#) What:   Creates a csv file over all scanned IP
    #@(#) lists each IP and all open/closed/filtered ports
    #@(#) list if hosts respons to 'advanced' ping
    #@(#) code 1 - recieved TCP/ACK ( open )
    #@(#) code 2 - Recieved FNI ACK (Closed)
    #@(#) code 3 - No response (filtered)
    #@(#)
    def generate_csv(self, output_filename):
        if not self.ping_file or not self.tcp_files:
            raise ValueError("Both ping and tcp XML files are required.")

        # Parse ping XML
        pingxml = NmapParser.parse_fromfile(self.ping_file)
        pinghost = {
            host.address: "11" if host.is_up() else "12"
            for host in pingxml.hosts
        }

        # Combine TCP XML data
        combined_hosts = self._combine_tcp_files()

        # Extract port and state information
        portid = [port for host in combined_hosts for port, _ in host.get_ports()]
        uniqueportlist = sorted(set(portid))

        ep = {
            host.address: {
                "filtered": "3",
                "closed": "2",
                "open": "1"
            }.get(host.extraports_state['state']['state'], "0")
            for host in combined_hosts
        }

        scandict = {}
        for host in combined_hosts:
            if host.is_up() and host.get_ports():
                tempdict = {serv.port: serv.state for serv in host.services}
                tlist = [
                    {"open": "1", "closed": "2", "filtered": "3"}.get(tempdict.get(p), "")
                    for p in uniqueportlist
                ]
                scandict[str(IPAddress(host.address))] = tlist

        # Write results to CSV
        with open(output_filename, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            header = ["Host", "Ping", "Ext ports"] + [str(port) for port in uniqueportlist]
            writer.writerow(header)

            for ip, port_states in scandict.items():
                row = [ip, pinghost.get(ip, ""), ep.get(ip, "")] + port_states
                writer.writerow(row)

        self.logger.debug(f"CSV file generated: {output_filename}")

# Example usage
if __name__ == "__main__":
    xmllist = ["20250116T130220_discovery_client1.ping.xml",
               "250116T130220_normal_client1.tcp.xml",
               "20250116T130220_full_client1.tcp.xml"
               ]
    generator = NmapCSVGenerator(xmllist)
    generator.generate_csv("output.csv")
