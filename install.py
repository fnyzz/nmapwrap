from pyaml import ConfigReader

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
#   ---- end of MinusPrint

def test(cfread):
#        approot = cfread.get("installation.root")
#        apphome = cfread.get("installation.home")
#        appresult = cfread.get("installation.nmapdata")
#        appuser = cfread.get("installatoin.username", 'nobody')
#        appexport = cfread.get("export.exportdir", 'export')
#        print(f"Installation root: {approot}")
#        print(f"App Home: {apphome}")
#        print(f"App Result: {appresult}")
#        print(f"App eport: {appexport}")
        ds = cfread.get("installation")
        for key, value in ds.items():
            print(f"{key}: {value}")



# Example usage
if __name__ == "__main__":
    config_file_path = "config.yaml"
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
