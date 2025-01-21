# <img src="images/Viking_Helmet.png" alt="Nmapwrap.py" style="width:5%; height:auto;"> Nmapwrap


This python program targets the automation of running nmap in a production environment where you are running the same nmap on schdule. Nmapwrap.py takes a configuration file on the YAML format and run the nmap with this configuration. First it runs a Nmap discovery scan based upon icmp ping and a list of port supplied by you. Online hosts are written to a file onlinehosts.TestClient.txt which the is used in a more thurow Nmap TCP scan. 


You may have different configuration files for different netsegments, clients etc. There is one standard config.yaml file which the reference to where nmap is installed, owner of the files etc. 
## 🌟 Features
- Repetable Nmap scan with the same parameter 
- Control Nmap parameter with yaml files 
- Audit trail of all nmap scans 
- Keep all 
- Run multiple Nmap scan without loosing logging

## ⚠️  Security 
Program runs as sudo (root). 
Running Nmap with the parameter -sS requiers root priveleges which is why I am skipping some input validation and why we run Python's popen sub process. 

The basic yaml config has 3 section: 
1. Name of the scan, where to store the data and a list of IP to scan. 
2. The discovery section 
3. The Nmap scan using hosts from the discovery section. 

The script uses the nmap binaries which is a pre requisite for this nmapwrapper to work. 

## 🚀 Quick Start, example run 
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

# That's all is needed to get started
```

## 📊 Usage

These are the command line option for you 
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


**The config.yaml file**  
This file lists: 
-where Nmap is installed 
*where you want the resulting Nmap data stoed 
+username and file persmission 



Example configuration:

```yaml
client:
  name: TestClient
  clienthome : /opt/nmapwrap/data/
  clientip: 10.0.0.0/24


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


nmap_normal:
  order: 2
  scan-type: normal
  suffix: tcp
  scanflag: -sS -n -PE
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

