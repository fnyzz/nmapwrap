
#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       nmapwrap
#@(#) ----------------------------------------------------------------
#@(#)           Purpose: Read the README.md file for details.
#@(#)           Author:  Ketil
#@(#)           year: 2025
#@(#)
#@(#) ----------------------------------------------------------------

from ConfigReader import ConfigReader
import optparse
import os
import sys
import logging
import time
import re
from time import strftime
from datetime import datetime
from Validator import Validator
from LogCreator import LoggerCreator
from DirManager import DirManager
from optparse import OptionParser
from UUIDGenerator import UUIDGenerator
from NmapRunner import NmapRunner
from SetPermission import SetPermission
from NmapParser import NmapParser
from NmapCSVGenerator import NmapCSVGenerator


nmapwrapConfig = "config/config.yaml"

#(@) + ----------------------------------------------
#(@) +
#(@) + Define and parse all the command line options
#(@) +
#(@) + ----------------------------------------------

parser=optparse.OptionParser('' )
print (" ")
epilog="""

examples of usage:

sudo ./main.py --config myclient.yaml
sudo ./main.py --config myclient.yaml --quiet


"""
optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog
parser=OptionParser(usage='%prog --config  <name of project> ', epilog=epilog)
parser.add_option('--quiet',action='store_true',  help='No output to std.out, only logfile ',dest='quiet')
parser.add_option(
    '-c',
    '--config',
    help='Name of the configuration file you want to use',
    dest='config')

(options,args)=parser.parse_args()
program = os.path.basename(sys.argv[0] )

#  +  -----------------------------------------------------------
#  +  Checking if the main configfile
#  +  exists
if not os.path.isfile(nmapwrapConfig):
    print (f"{now} Error: Need the std yaml config file! {nmapwrapConfig}")
    sys.exit(99)

def main (argv):
    #  +  -----------------------------------------------------------
    #  +  Checking if we have a spesific config file.
    now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    if options.config:
        ClientConfigFile = options.config
    else:
        print (f"{now} Error: Need a yaml config file as an option. See help for info")
        sys.exit(99)

    if not Validator(nmapwrapConfig).is_valid_filedir():
        print (f" {now} Illegal charachter in input filename " )
        sys.exit(99)

    try:
        #(@) +  -----------------------------------------------------------
        #(@) + Reading the std config.yaml file
        #(@) + Reading the client yaml config file
        #(@) + Merge into one dictionary
        config_reader = ConfigReader(nmapwrapConfig,ClientConfigFile)
        mconfig = config_reader.merge_configs()

        #(@) +  -----------------------------------------------------------
        #(@) +  Getting new UUID
        #(@) +  This is used to identify each scan in log files.
        uuid_generator = UUIDGenerator()
        unique_id = uuid_generator.generate_uuid()

        #(@) +  -----------------------------------------------------------
        #(@) +  Getting the log dir and filename from dict
        log_dir = mconfig['logging']['dir']
        log_file= mconfig['logging']['file']
        log_level=mconfig['logging']['level']

        #(@) +  -----------------------------------------------------------
        #(@) +  Setting up a default log handler, where all program logs are written
        #(@) +  Log directory and file is created if not exists
        #(@) +  This file is not currently rotated.
        logger_creator = LoggerCreator(log_dir, log_file,log_level,unique_id,options.quiet )
        logger = logger_creator.get_logger(program)
        logger.info("Program start" )
        logger.debug("directories: %s %s %s ", log_dir, log_file, log_level)

        #(@) +  -----------------------------------------------------------
        #(@) +  reading app name and version
        appname = mconfig['app']['name']
        appver  = mconfig['app']['version']
        appenv  = mconfig['app']['environment']
        logger.debug("App data: {appname}  {appver} {appenv}" )

        #(@) + ----------------------------------------------
        #(@) + Checking if source from config.yaml is installed
        #(@) + This would be nmap
        #(@) + This would be rsync (not currently in use; will be shortly)
        dsources = mconfig.get('sources',{})
        logger.debug("Checking binaries and ports.yaml file" )
        for i,j in dsources.items():
            if not os.path.isfile(j):
                logger.error(f"Requiered program {j} is not installed ")
                logger.info("Bailing out!!" )
                sys.exit()

        #(@) + ----------------------------------------------
        #(@) + Checking environment from config/config.yaml
        #(@) + exists. If not => create it
        manager = DirManager(mconfig,logger=logger)

        try:
            #(@) + ----------------------------------------------
            #(@) + creating Linux environment
            #(@) + setting the correct access rights.
            manager.manage_directories()
            sessionID = strftime("%Y%m%dT%H%M%S")
            xmlList = []

            #(@) + ----------------------------------------------
            #(@) + Reading all entried from dict which starts with nmap_ #nmap config
            #(@) +         sorting the entris based upon the key order
            #(@) + Getting the client info
            #(@) + Getting path to nmap binaries
            #(@) +
            nmapconfig = {key: value for key, value in mconfig.items() if key.startswith('nmap_')}
            sorted_nmapconfig = dict(sorted(nmapconfig.items(), key=lambda item: item[1]['order']))
            ClientDict = mconfig.get("client")
            NmapBIN    = mconfig.get("sources", {}).get("nmap")

            #(@) + ----------------------------------------------
            #(@) + Looping over all the different Nmap settings
            #(@) + There has to be at least 2
            #(@) + a discovery
            #(@) + a TCP scan
            for i,dictnmapcfg in sorted_nmapconfig.items():
                #(@) + ----------------------------------------------
                #(@) + creating a class for running Nmap
                #(@) + executing that class.
                #(@) + return from class: 2 filenames:
                #(@) + a filename for online host should be stored
                #(@) + a filename of the nmap XML data
                runner = NmapRunner(ClientDict, NmapBIN, dictnmapcfg, sessionID, logger)
                online_filename,x_file = runner.run()
                xml_filename = x_file +".xml"
                xmlList.append(xml_filename)
                #(@) + ----------------------------------------------
                #(@) + geonlinehosts => if this is set in yaml config file
                #(@) + then we find all host which was online from ping scan
                if dictnmapcfg.get('genonlinehosts'):
                    #(#) + --------------------------------------------------------------------------
                    #(#) + grab all hosts which is alive from the ping.xml file
                    #(#) + run
                    parser = NmapParser(xml_filename)
                    parser.write_alive_hosts_to_file(online_filename)
                #else:
                #    print(f"Getting open ports from {xml_filename}")

            #(#) + -----------------------------------------
            #(#) + Getting

            user_info = mconfig.get('uid',{})
            CLName = mconfig.get('client',{}).get('name')
            d = mconfig.get('client',{}).get('clienthome')
            dirsub = re.sub(r'/$', '', d)
            #directory = d + "/" + CLName
            directory = dirsub + "/" + CLName

            #(#) + -----------------------------------------
            #(#) + Creating a CSV file based up on
            #(#) + ping.xml and all tcp.xml
            #(#) +
            logger.debug(f"XML files: {xmlList}")
            CSVfile = directory + "/" + strftime("%Y%m%d") +"." +CLName +".csv"
            generator = NmapCSVGenerator(xmlList)
            generator.generate_csv(CSVfile)

            #(#) + -----------------------------------------
            #(#) + Cleaning up user and access rights.
            logger.debug (f" SetPermission with thisinfo : {mconfig.get('uid',{})}")
            logger.debug (f" SetPermission with thisinfo : {directory}")
            permission_setter = SetPermission(user_info, directory, logger)
            permission_setter.set_permissions()

        except SystemExit as e:
            logger.warning(f"Directory management failed with exit code: {e.code}")
            sys.exit()

        logger.info("Program stop successfully" )

    except Exception as e:
        print(f"{now} Exception Error: {e}")


if __name__ == "__main__":
    main(sys.argv)
