

from pyaml import ConfigReader
from optparse import OptionParser
import optparse, concurrent
import sys
import os

parser=optparse.OptionParser('' )
# print " "
epilog="""
       """

optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog
parser=OptionParser(usage='%prog --config <configuration file> ', epilog=epilog)
parser.add_option('--config', help='Configurasjon file',dest='cfile')


(options,args)=parser.parse_args()
program = os.path.basename(sys.argv[0] )


#@(#) ----------------------------------------------------------------
#@(@) funtion name: is_real_root
#@(#) input: none
#@(#) return: true/false
#@(#) What: checks if the current user is root or runs as root (sudo)
#@(#)
def is_real_root():
    user = os.getenv("USER")
    sudo_user = os.getenv("SUDO_USER")
    print (f"We recommend running with sudo ") if str(sudo_user == "root") else None
    return user == "root" or str(sudo_user) == "root"
#   + -------- end is_real_root


#@(#) ----------------------------------------------------------------
#@(@) funtion name: creatdir
#@(#) input: Path
#@(#) return:
#@(#) What: Checks and creates std. production environment.
#@(#)
def creatDir(path):
    mode = 0o755
    if not os.path.exists(path):
        try:
            os.mkdir(path, mode )
            if (( os.getenv("USER") == "root" ) and (str ( os.getenv("SUDO_USER"))  != "None")):
                uid = int(getpwnam(os.getenv("SUDO_USER"))[2])
                u   = os.getenv("SUDO_USER")
                gid = int(pwd.getpwnam(u).pw_gid)
                os.chown(path, uid, gid);
            if ( options.debug ):
                MinusPrint ('  Created catalog ' , path)
        except os.error as error :
            print (error)
#   + -------- end creatDir

def test(cfread):
        approot = cfread.get("installation.root")
        apphome = cfread.get("installation.home")
        appresult = cfread.get("installation.nmapdata")
        appuser = cfread.get("installatoin.username", 'nobody')
        appexport = cfread.get("export.exportdir", 'export')
        print(f"Installation root: {approot}")
        print(f"App Home: {apphome}")
        print(f"App Result: {appresult}")
        print(f"App eport: {appexport}")
        ds = cfread.get("installation")
        for key, value in ds.items():
            print(f"{key}: {value}")

#+ ------------------------------------------------------------------------------- + #
# + functoin: main
# + descr   : The main function
# + ------------------------------------------------------------------------------- + #
def main (argv):
    #  +  -------------
    #  +  program needs to run as root
    #  +  we prefer running as sudo
    if not is_real_root():
       print(f"This program needs to run as root" )
       sys.exit()

    try:
       # Setting up a log handler for handling logging

       if options.cfile:
           print (f"Reading the configuration file: {options.cfile} ")
           # 1. validate cfg-file content
           # 2. chk environment listed in the cfg file
           # 3.
           config_file_path = options.cfile
           config_reader = ConfigReader(config_file_path)
           try:
               config_reader.load_config()
               appname = config_reader.get("app.name")
               appver  = config_reader.get("app.version")
               appenv  = config_reader.get("app.environment")
               print (f"Application name: {appname}")
               print (f"Application version: {appver}")
               print (f"Application environemnt: {appenv}")
               test(config_reader)
           except Exception as e:
               print(f"ERROR: Reading {options.cfile} failed: {e}")

       else:
           print(f"Illegal options. Maybe try --help as an option!")
    except Exception as e:
        # Roll back any change if something goes wrong
        # db.rollback()
        # print ( "Exception caught: raise e:%s ", e )
        print(f"Error, giving up back:%s ", e)
    finally:
        # Close the db connection
        print(f"Finally: exiting !")
        # db.close()
        sys.exit()



#+ ------------------------------------------------------------------------------- + #
# + functoin: Call main
# + descr   : runs the main function
# + ------------------------------------------------------------------------------- + #
if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print (f"Interupted", datetime.datetime.now())
        sys.exit(0)
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)




        #approot = config_reader.get("installation.root")
        #apphome = config_reader.get("installation.home")
        #appresult = config_reader.get("installation.nmapdata")
        #appuser = config_reader.get("installatoin.username", 'nobody')
        #appexport = config_reader.get("export.exportdir", 'export')
        #print(f"Installation root: {approot}")
        #print(f"App Home: {apphome}")
        #print(f"App Result: {appresult}")
        #print(f"App eport: {appexport}")
        #print(f"Installation user: {appuser}")
    except Exception as e:
        print(f"Error: {e}")
