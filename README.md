# <img src="images/Viking_Helmet.png" alt="Nmapwrap.py" style="width:5%; height:auto;"> Nmapwrap


This python program targets the automation of running nmap in a production environment where you are 
running the same nmap on schdule towards several different networks. 
Nmapwrap.py takes a configuration file on the YAML format and run  the nmap with this configuration. 
First it runs a Nmap discovery scan based upon icmp ping and a list of port supplied by you. 
Online hosts are written to a file onlinehosts.TestClient.txt which  the is used in next scan which is 
TCP scan towards online hosts. 


You may have different configuration files for different netsegments, clients etc. There is one standard config.yaml file which the reference to where nmap is installed, owner of the files etc. 
## 🌟 Features
- Repetable Nmap scan with the same parameter  easily configured in yaml config files 
- Control Nmap parameter with yaml files 
- Audit trail of all nmap scans 
- Name nmap result file on a logical basis
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

```


# <img src="images/Viking_hammer.png" alt="User configuration yaml file" style="width:5%; height:auto;">Creating your own yaml file
You should have one configuration file for each logical net-segment you want to scan or for a spesific service. What's important is that you have at least two section. One where you do nmap discovery and one for the TCP scan. You can have more than one TCP scan. When you are scanning networks which are slow and you need to get a prelimmarary result, you could run a top-ports 1024, before you run the full TCP scan with 65535 ports.  

# This is what you have to change in your own yaml files:  

Change the name stansa to the what you want to call this configuration. Choose where to store the files and enter your IP list 
```yaml
client:
   name: TestClient
   clienthome : /opt/nmapwrap/data/
   clientip: 10.0.0.0/24
```

You can keep the nmap_discovery as is. If you want to do less ports for TCP discovery, go ahead and change the port list. 

The next section, 

```yaml
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
```



# <img src="images/Viking_boat_2x.png" alt="Nmapwrap Flow" style="width:5%; height:auto;"> Nmapwrap program flow 

This 
s the program flow of the nmapwrap.py: 
1. The config/config.yaml file is read together with the --config option file and merged into a dictionary 
2. The target directories are then check if exists and created if not 
3. The 


