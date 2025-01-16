import xml.etree.ElementTree as ET

class NmapParser:
    def __init__(self, input_filename):
        self.input_filename = input_filename
        print (f"input: {self.input_filename}")

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

    def write_alive_hosts_to_file(self, output_filename):
        alive_hosts = self.get_alive_hosts()
        with open(output_filename, 'w') as f:
            for host in alive_hosts:
                print(f"hosts {host}")
                f.write(f"{host}\n")

# Usage example
if __name__ == "__main__":
    #input_filename = "20250113T093845_discovery_FullerLN.ping.xml"  # Replace with your actual input file name
    #output_filename = "alive_hosts.txt"  # Replace with your desired output file name
    input_filename = "/opt/nmapwrap/data/FullerLN/20250115T183636_discovery_FullerLN.ping.xml"
    output_filename ="/opt/nmapwrap/data/FullerLN/onlinehosts.FullerLN.txt"

    parser = NmapParser(input_filename)
    parser.write_alive_hosts_to_file(output_filename)

