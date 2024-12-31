
#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2025 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       main
#@(#) ----------------------------------------------------------------
#@(#)           $Author: Ketil $
#@(#)           Purpose: wrapper for nmap and create output on std. format.
#@(#)           Directions: run nmap scan the Werfen way
#@(#)     Invoked by:  Ketil
#@(#) ----------------------------------------------------------------

from ConfigReader import ConfigReader
import optparse
import os
import sys
import logging
from LinuxPathValidator import LinuxPathValidator



#(@) + ----------------------------------------------
#(@) +
#(@) + Define and parse all the command line options
#(@) +
#(@) + ----------------------------------------------

parser=optparse.OptionParser('' )
print (" ")
epilog="""

examples of usage:
scan a few ports:
sudo ./wilscan959.py -c "t-0345_my_hackingfactory "  -i "10.1.2.31"  -p "34, 45, 56, 80, 445 " -d -P

"""
optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog

parser.add_option(
    '-c',
    '--config',
    help='Name of the configuration file you want to use',
    dest='config')

(options,args)=parser.parse_args()
program = os.path.basename(sys.argv[0] )


def main (argv):

    #  +  -----------------------
    #  +  Checking if we have a spesific config file.
    if options.config:
        config_file_path = options.config
        # print (f"config file {config_file_path}")
    else:
        print (f"Error: Need a yaml config file")
        sys.exit(99)
    if not LinuxPathValidator(config_file_path).is_valid():
        print ("Illegal charachter in input filename " )
        sys.exit()

    config_reader = ConfigReader(config_file_path)
    try:
        config_reader.load_config()
        appname = config_reader.get("app.name")
        appver  = config_reader.get("app.version")
        appenv  = config_reader.get("app.environment")
        print (f"Application name: {appname}")
        print (f"Application version: {appver}")
        print (f"Application environemnt: {appenv}")


        instroot = config_reader.get("installation")
        #help(instroot)
        print (f" Environment: {config_reader.get('installation.root')} ")


        approot = config_reader.get("installation.root", "/opt/nmapwrap")
        appuser = config_reader.get("installatoin.username", 'nobody')
        print(f"Installation root: {approot}")
        print(f"Installation user: {appuser}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main(sys.argv)
