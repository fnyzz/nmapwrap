# Nmap Wrapper for automation
# nmapwrapper 

This python program targets the automation of running nmap in a production environment. It takes a configuration file on the YAML format and run the nmap with this configuration. You may have different configuration files for different netsegments, clients etc. The are differnet reason you want to run nmap using this wrapper. 
- Audit trail of all nmap scans 
- Logging of all scans in one place 
- History of nmap result 
- 
The script uses the nmap binaries which is a pre requisite for this nmapwrapper to work. 


# example run 
```sh
$ sudo ./nmapwrap.py  --config myclient.yaml 
```

**Installation**
```sh
# Download the repo from githug: 
$ git clone https://github.com/fnyzz/nmapwrap.git 

# Install nmap online:
$ apt-get install nmap

$ pip3 install -r requirements.txt



# That's all is needed to get started
```
