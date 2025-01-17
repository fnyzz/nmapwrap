# nmapwrapper 

This python program targets the automation of running nmap in a production environment. It takes a configuration file on the YAML format and run the nmap with this configuration. You may have different configuration files for different netsegments, clients etc. There is one standard config.yaml file which the reference to where nmap is installed, owner of the files etc. 

There are differnet reason you want to run nmap using this wrapper. 
- Audit trail of all nmap scans 
- Logging of all scans in one place 
- Repetable Nmap scan with the same parameter 
- History of nmap result 
- 
The script uses the nmap binaries which is a pre requisite for this nmapwrapper to work. 


# example run 
```sh
$ sudo python3 ./nmapwrap.py  --config config/myclient.yaml 
```

**Installation**
```sh
# Create a virtual environment where you install Python: 
$ python -m venv ~/venv 

# Download the repo from githug: 
$ 
$ git clone https://github.com/fnyzz/nmapwrap.git 

# Install nmap online:
$ apt-get install nmap

# install all dependensis listen in requirements
$ pip3 install -r requirements.txt

# initiate the virtual python environment: 
$ source ~/venv/bin/activate
$ cd ~/nmapwrap 
$ sudo python3 ./nmapwrap.py --config config/MyNetwork.yaml 

# Run nmapwrap.py like this: 
$ sudo ~/
# That's all is needed to get started
```


