import csv
from netaddr import IPAddress
from libnmap.parser import NmapParser

class NmapCSVGenerator:
    def __init__(self, xmllist):
        """
        Initialize the generator with a list of XML files.
        :param xmllist: List of XML files (ping and tcp files).
        """
        self.xmllist = xmllist
        self.ping_file = None
        self.tcp_files = []
        self._separate_files()

    def _separate_files(self):
        """
        Separate ping and tcp files from the input list.
        Assumes one ping file and multiple tcp files.
        """
        for file in self.xmllist:
            if file.endswith("ping.xml"):
                self.ping_file = file
            elif file.endswith("tcp.xml"):
                self.tcp_files.append(file)

    def _combine_tcp_files(self):
        """
        Combine all TCP XML data into a single list of hosts.
        :return: Combined list of hosts from all TCP files.
        """
        combined_hosts = []
        for tcp_file in self.tcp_files:
            parsed_data = NmapParser.parse_fromfile(tcp_file)
            combined_hosts.extend(parsed_data.hosts)
        return combined_hosts

    def generate_csv(self, output_filename):
        """
        Generate a CSV file from the combined XML data.
        :param output_filename: Name of the output CSV file.
        """
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

        print(f"CSV file generated: {output_filename}")

# Example usage
if __name__ == "__main__":
    xmllist = ["/opt/nmapwrap/data/FullerLN/20250116T130220_discovery_FullerLN.ping.xml",
               "/opt/nmapwrap/data/FullerLN/20250116T130220_normal_FullerLN.tcp.xml",
               "/opt/nmapwrap/data/FullerLN/20250116T130220_full_FullerLN.tcp.xml"
               ]
    generator = NmapCSVGenerator(xmllist)
    generator.generate_csv("output.csv")
