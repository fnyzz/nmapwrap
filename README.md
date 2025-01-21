# <img src="images/Viking_Helmet.png" alt="Nmapwrap.py" style="width:5%; height:auto;"> Nmapwrap

NmapWrap is a Python-based tool designed to automate Nmap scanning in production environments, where scheduled scans target multiple networks. Using a YAML configuration file, NmapWrap performs two key scans:

1. Discovery Scan: Identifies online hosts via ICMP ping and user-specified ports. The results are saved to a file (e.g., onlinehosts.TestClient.txt).
2. TCP Scan: Performs in-depth scans on the online hosts identified in the discovery phase.
This structure enables you to manage separate YAML configuration files for different network segments, clients, or services, all while maintaining a standard config.yaml for global settings like file ownership and Nmap installation paths.

## 🌟 Features
- Repetable Nmap scan with the same parameter  easily configured in yaml config files 
- Control Nmap parameter with yaml files 
- Audit trail of all nmap scans 
- Name nmap result file on a logical basis
- Run multiple Nmap scan without loosing logging

## ⚠️  Security 
Program runs as sudo (root). 
Running Nmap with the parameter -sS requiers root priveleges which is why I am skipping some input validation and why we run Python's popen sub process. 

# <img src="images/Viking_boat_2x.png" alt="Nmapwrap Flow" style="width:5%; height:auto;"> Nmapwrap program flow 
This is the program flow of the nmapwrap.py: 
1. The config/config.yaml file is read together with the --config option file and merged into a dictionary 
2. The target directories are then check if exists and created if not 
3. We sort all the nmap configed according to the order stansa. All Nmap configs should start with nmap_
4. We loop over all these nmap configuration, creats the nmap commandline and run nmap 
5. We create a CSV file containing alive hosts and availabl eservice. 



## 🚀 Quick Start 
There are two yaml config files. One called config.yaml where you 
- spesify the user name who will own the nmap files 
- list the full path to where nmap is installed 
- where you want the nmap data to be stored. 

Then there is the input option --config config/TestClient.yaml 
The yaml config has 3 section: 
1. Name of the scan, where to store the data and a list of IP to scan. 
2. The Nmap discovery section. You may add more than one section where you do 
3. The Nmap section where you spesify what ports to scan etc. 

```sh
$ sudo python3 ./nmapwrap.py  --config config/myclient.yaml 
```

**Installation**
```bash
# Create a virtual environment where you install Python: 
$ python -m venv ~/venv 

# Download the repo from githug: 
$ git clone https://github.com/fnyzz/nmapwrap.git 
$ cd ~/nmapwrap 

# Install nmap online:
$ apt-get install nmap

# install all dependensis listen in requirements
$ pip3 install -r requirements.txt

# initiate the virtual python environment: 
$ source ~/venv/bin/activate

# Run nmapwrap.py like this: 
$ sudo python3 ./nmapwrap.py --config config/MyNetwork.yaml 

# That's all is needed to get started. REMEMBER to checkout how to setup the MyNetwork.yaml files down below. 
```

## 📊 Usage
Before you run the program, you should change the username in the config/config.yaml file to your own user or the user you want to be the owner of the resulting nmap files. 
Then create your own yaml files spesifying what you want to scan, nmap parameters etc. You may copy one the example yaml files provided in the project. 

There is only one option for interactive run, which is where your yaml config file is. If you do not want any output to the console, use --quiet. Use this option when running in crontab. 

```bash 
# python3 ./nmapwrap.py --help


Usage: nmapwrap.py --config  <name of project>

Options:
  -h, --help            show this help message and exit
  --quiet               No output to std.out, only logfile
  -c CONFIG, --config=CONFIG
                        Name of the configuration file you want to use


examples of usage:

sudo ./nmapwrap.py --config config/myclient.yaml
sudo ./nmapwrap.py --config config/myclient.yaml --quiet
```


** Example configuration ** 

```yaml
client:
  name: internal_full
  clienthome : /opt/nmapwrap/data/
  clientip: 10.0.0.0/24

#  +  ----------------------------------------------------------------
#  +  nmap discover settings
#  +  Called Ping scan. This detects host on the network.
#  +  If the ICMP ping does not discover the host, then
#  +  Nmap will run a tcp ping on the spesified ports.
#  +  Add/delete ports which fits your environment.
#  +  NB! important! host may be online if none of these ports are
#  +  reachable. Should always know your environment before scanning
#  +  Change ports to suite your needs.
#  +  ----------------------------------------------------------------
nmap_discoverycfg:
  order: 1
  scan-type: discovery
  suffix: ping
  genonlinehosts: True
  scanflag: -sn -n -PE
  max-hostgroup: 150
  max-retries: 4
  min-rtt-timeout: 100ms
  initial-rtt-timeout: 500ms
  scan-delay: 2ms
  max-scan-delay: 20ms
  min-rate: 450
  max-rate: 15000
  max-rtt-timeout: 50ms
  reports: -oA
  ports:  -PS21-23,25-26,53,80-81,110-111,113,135,139,143,443,445,465
          ,514-515,587,993,995,1025-1026,1433,3306,3389,5060,5432,5900
          ,6000,6881,8000,8008,8080,8443

#  +  ----------------------------------------------------------------
#  +  nmap Normal scan
#  +  we scan the top 4000 ports
#  +  ----------------------------------------------------------------
nmap_normal:
  order: 2
  scan-type: normal
  suffix: tcp
  scanflag: -sS -n
  max-hostgroup: 150
  max-retries: 4
  min-rtt-timeout: 100ms
  initial-rtt-timeout: 500ms
  scan-delay: 2ms
  max-scan-delay: 20ms
  min-rate: 450
  max-rate: 15000
  max-rtt-timeout: 50ms
  reports: -oA
  top-ports: 500

#  +  ----------------------------------------------------------------
#  +  nmap TOP 1000 ports
#  +  We scan top 1000 ports
#  +
#  +  ----------------------------------------------------------------
nmap_top1000:
  order: 3
  scan-type: top1000
  suffix: tcp
  scanflag: -sS -n
  max-hostgroup: 150
  max-retries: 4
  min-rtt-timeout: 100ms
  initial-rtt-timeout: 500ms
  scan-delay: 2ms
  max-scan-delay: 20ms
  min-rate: 450
  max-rate: 15000
  max-rtt-timeout: 50ms
  reports: -oA
  ports: -p 1-1024


#  +  ----------------------------------------------------------------
#  +  nmap Full
#  +  We scan ALL 65535 ports
#  +
#  +  ----------------------------------------------------------------
nmap_Full:
  order: 4
  scan-type: full
  suffix: tcp
  scanflag: -sS -n
  max-hostgroup: 150
  max-retries: 4
  min-rtt-timeout: 100ms
  initial-rtt-timeout: 500ms
  scan-delay: 2ms
  max-scan-delay: 20ms
  min-rate: 450
  max-rate: 15000
  max-rtt-timeout: 50ms
  reports: -oA
  ports: -p-
```


# <img src="images/Viking_hammer.png" alt="User configuration yaml file" style="width:5%; height:auto;">CSV file explenation 


The table in the CSV file provides an overview of the available ports on the servers involved in the test. The explanation of the table is as follows:

- 1 The port is open and responds with a SYN-ACK to our request.
- 2 The port is closed on the machine and responds with a RESET-ACK to our request.
- 3 The port does not respond, likely because the firewall is dropping our request.
- 7 The port responds to UDP requests.
- 8 The port does not respond to UDP requests.
- 11 The machine responds to ping requests.
- 12 The machine does not respond to ping requests.

The "Default" column shows the response for all other scanned ports that are not included in the table. Blank fields in the table have the same status as the "Default" column.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE.txt) file for details.

