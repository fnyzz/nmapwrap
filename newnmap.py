#!/usr/bin/env python3
#@(#)________________________________________________________________
#@(#)________________________________________________________________
#@(#)
#@(#) Copyright(C) 2023 fnyxzz
#@(#) All rights reserved.
#@(#)
#@(#) Use and distribution of this software and its source code
#@(#) are governed by the terms and conditions of the
#@(#) fnyxzz lisence ("LICENSE.TXT")
#@(#) ----------------------------------------------------------------
#@(#) Name      :       wilscan959
#@(#) ----------------------------------------------------------------
#@(#)              $Source:  git$
#@(#)            $Revision:  1.9$
#@(#)                $Date: Wed Feb  8 20:51:21 EST 2023$
#@(#)              $Author: Ketil $
#@(#)              $Locker: koh $
#@(#)               $State: Exp $
#@(#)
#@(#)              Purpose: wrapper for nmap and create output on std. format.
#@(#)
#@(#)           Directions: run nmap scan the Werfen way
#@(#)
#@(#)     Default Location:
#@(#)     Invoked by:  Ketil
#@(#) ----------------------------------------------------------------
from libnmap.parser import NmapParser
from netaddr import *
import platform
import sys
import re
import argparse
import os
import subprocess
import time
import pwd
import datetime
import optparse
import socket
import pymsteams
from time import gmtime, strftime
from optparse import OptionParser
from pwd import getpwnam
from xml.dom import minidom
from loggerinitializer import *
from oalib import is_valid_url
import logging



WideAngle="/opt/werfen/results"
defaulttimeout=""
ccustomer=""
webhook=""
tnull=time.time()

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

scan all 65535 ports with P0 option:
sudo ./wilscan959.py -c "il16-2345_gem5000"  -i "10.1.2.31"  -p F -P

scan 4k port with P0 option
sudo ./wilscan959.py -c "il16-2345_gem5000"  -i "10.1.2.31"  -p N -P

scan opnly host which are online with 4k ports, print out debug infomation
sudo ./wilscan959.py -c "il16-2345_gem5000myphonecompany"  -i "10.1.2.31"  -p N --debug

scan opnly host which are online with 4k ports and a UDP scan
sudo ./wilscan959.py -c "il16-2345_gem5000myphonecompany"  -i "10.1.2.31"  -p N --udp

scan opnly host which are online with 4k ports, alert in MSTeams
sudo ./wilscan959.py -c "il16-2345_gem5000myphonecompany"  -i "10.1.2.31"  -p N --alert

This script is documented in Confluence:
    https://jira.ilww.com:8099/confluence/display/CYB/Nmap+scanning

copyright(c) 2023 fnyxzz production\

"""
optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog


parser=OptionParser(usage='%prog -c <name of project> -i "ip-adresses" -p <choise of ports> -t <time out value>', epilog=epilog)
parser.add_option('-c','--config', help='Name of customers configuration file on YAML format',dest='customer')
#parser.add_option('-a','--alert', action='store_true', help='If you want to be alerted into MSTeam then you may use this options. The file webhook file, /opt/werfen/cfg/nmapMSteam.hook.txt is hardcoded ( for now). We will get a MS Teams msg when the wilscan959 is done')
#parser.add_option('-u','--udp', action='store_true', help='Use -u or --udp if you also want to run UDP scan. UDP scan can be more inaccurate especially on the Internet where we have to cross a Firewall. FW seems to stop a lot of UDP traffic and then we will end up with a lot of false positive.',dest='udp')
parser.add_option('-d','--debug',action='store_true',help='Print debug information')


#@(#) ----------------------------------------------------------------
#@(@) funtion name: PlusPrint
#@(#) input: Text and value
#@(#) return: none
#@(#) What: Print test to std.out
#@(#)
def PlusPrint(d,c):
    #sys.stdout.write('[+] ' + text )
    print ('[+] -' + d + '\033[0;32m'+c+'\033[00m' )
#   ---- end of PlusPrint

#@(#) ----------------------------------------------------------------
#@(@) funtion name: MinusPrint
#@(#) input: Text and value
#@(#) return: none
#@(#) What: Print test to std.out
#@(#)
def MinusPrint(d,c):
    print (' [-] ->' + d + '\033[0;32m'+c+'\033[00m' )
#   ---- end of MinusPrint


(options,args)=parser.parse_args()
program = os.path.basename(sys.argv[0] )

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

#@(#) ----------------------------------------------------------------
#@(@) funtion name: CheckPath
#@(#) input: Path
#@(#) return:
#@(#) What: Checks and creates std. production environment.
#@(#)
def CheckPath(path):
    mode = 0o755
    if not os.path.exists(path):
        if ( options.debug ):
            MinusPrint('  creating environment: ', path)
        l=[]
        p = "/"
        l = path.split("/")
        i = 1
        while i < len(l):
            p = p + l[i] + "/"
            i = i + 1
            if not os.path.exists(p):
                try:
                   os.mkdir(p, mode )
                   if (( os.getenv("USER") == "root" ) and (str ( os.getenv("SUDO_USER"))  != "None")):
                       uid = int(getpwnam(os.getenv("SUDO_USER"))[2])
                       u   = os.getenv("SUDO_USER")
                       gid = int(pwd.getpwnam(u).pw_gid)
                       os.chown(p, uid, gid);
                   if ( options.debug ):
                       MinusPrint ('  Created catalog ' , p)
                except os.error as error :
                   print (error)
    else:
        if ( options.debug ):
            MinusPrint ('  deleting old files in ' , path )
        for root, dirs, files in os.walk(path):
            for currentFile in files:
                exts=('.gnmap', '.nmap', '.txt')
                if any(currentFile.lower().endswith(ext) for ext in exts):
                    try:
                        os.remove(os.path.join(root, currentFile))
                        if ( options.debug ):
                            MinusPrint ('   deleting file: ' , currentFile)
                    except os.error as e:
                        print (e)

    return True


#@(#) ----------------------------------------------------------------
#@(@) funtion name: getports
#@(#) input: Type of ports needed.
#@(#) return: a list of ports
#@(#) What: Returns a list of ports depend on what the yser wants,
#@(#) F=all , N=4000+normal ports,
def getports(typeofports):
    if ( options.debug ):
        PlusPrint ('  getting ' , typeofports + ' ports')
    # open cfg file with discoverports
    # if file does not exists, use this ports as a std.
    return_ports=0

    if ( typeofports == "discover"):
        return_ports = "-PS21-23,25-26,53,80-81,110-111,113,135,139,143,179,199,443,445,465,514-515,548,554,587,993,995,1025-1026,1433,1720,1723,2000-2001,3306,3389,5060,5432,5900,6001,6881,8000,8008,8080,8443,8888,10000,32768,49152,49154 -PU53,67-69,111,123,135,137-139,161-162,445,500,514,520,631,1434,1900,4500,5353,49152,49154 "

    if ( typeofports == "quickscan"):
        return_ports = "21-23,25,53,79-80,109-111,113,137-139,443,445,8080"

    if ( typeofports == "normal"):
        # check if portfile exists, if not return
        return_ports = "1-4096,\
        ,4100,4132,4133,4144,4201,4242,4321,4333,4343,4353,4444,4488,4500,4523,4545,4555,4557,4559,4567,4590,4653,4666,4672,4777,4888,\
        4950,4999,5000,5001,5002,5005,5010,5011,5025,5031,5032,5050,5060,5111,5145,5190,5191,5192,5193,5222,5232,5236,5300,5301,5302,5303,\
        5304,5305,5308,5321,5333,5343,5400,5401,5402,5405,5432,5444,5503,5510,5512,5520,5521,5530,5534,5540,5550,5555,5556,5557,5569,\
        5631,5632,5637,5638,5666,5680,5713,5714,5715,5716,5717,5741,5742,5760,5777,5800,5801,5802,5873,5880,5882,5888,5889,5900,5901,\
        5902,5977,5978,5979,5985,5986,5997,5998,5999,6000,6001,6002,6003,6004,6005,6006,6007,6008,6009,6050,6065,6105,6106,6110,6111,6112,6141,\
        6142,6143,6144,6145,6146,6147,6148,6222,6272,6333,6346,6400,6444,6502,6555,6558,6661,6666,6667,6668,6669,6670,6671,6672,6673,\
        6674,6699,6711,6712,6713,6723,6767,6771,6776,6777,6838,6883,6888,6912,6939,6969,6970,6999,7000,7001,7002,7003,7004,7005,7006,\
        7007,7008,7009,7010,7028,7100,7111,7158,7200,7201,7215,7222,7300,7301,7306,7307,7308,7326,7333,7424,7444,7555,7579,7597,7626,\
        7666,7718,7777,7789,7826,7888,7891,7983,8000,8007,8009,8080,8081,8082,8111,8192,8210,8222,8333,8443,8444,8555,8666,8685,8777,\
        8787,8812,8879,8888,8892,8988,8989,8999,9000,9001,9002,9003,9004,9005,9065,9090,9091,9100,9111,9222,9325,9333,9400,9444,9535,\
        9555,9601,9602,9603,9604,9666,9777,9870,9871,9872,9873,9874,9875,9876,9877,9878,9888,9889,9890,9891,9892,9893,9894,9895,9896,\
        9897,9898,9899,9900,9901,9902,9903,9904,9905,9906,9907,9908,9909,9910,9911,9912,9913,9914,9915,9916,9917,9918,9919,9920,9921,\
        9922,9923,9924,9925,9926,9927,9928,9929,9930,9931,9932,9933,9934,9935,9936,9937,9938,9939,9940,9941,9942,9943,9944,9945,9946,\
        9947,9948,9949,9950,9951,9952,9953,9954,9955,9956,9957,9958,9959,9960,9961,9962,9963,9964,9965,9966,9967,9968,9969,9970,9971,\
        9972,9973,9974,9975,9976,9977,9978,9979,9980,9981,9982,9983,9984,9985,9986,9987,9988,9989,9991,9992,9999,10000,10005,10008,\
        10022,10067,10082,10083,10085,10086,10100,10101,10167,10498,10520,10528,10607,10666,11000,11050,11051,11111,11223,11371,11831,\
        12000,12076,12222,12223,12310,12345,12346,12347,12348,12349,12361,12362,12363,12456,12623,12624,12631,12701,12754,13000,13010,\
        13013,13014,13223,13333,13473,13700,14000,14444,14500,14501,14502,14503,15000,15092,15104,15382,15555,15858,16000,16384,16484,\
        16660,16666,16772,16959,16969,17000,17007,17166,17300,17449,17499,17500,17569,17593,17777,18000,18231,18264,18667,18753,18888,\
        19000,19864,19999,20000,20001,20002,20003,20004,20005,20023,20034,20203,20331,20432,20433,21000,21001,21002,21003,21004,21005,\
        21006,21007,21008,21009,21010,21111,21544,21554,21579,21957,22000,22222,22273,22289,22305,22321,22370,23000,23005,23006,23023,\
        23032,23321,23333,23432,23456,23476,23477,23777,24000,24289,24444,25000,25123,25555,25685,25686,25982,26000,26208,26274,26666,\
        26681,27000,27160,27374,27444,27573,27665,27777,28000,28431,28678,28792,28793,28794,28795,28796,28797,28798,28888,29000,29104,\
        29292,29369,29559,29891,29999,30000,30001,30002,30003,30004,30005,30029,30070,30100,30101,30102,30103,30133,30303,30700,30947,\
        30999,31000,31111,31221,31335,31336,31337,31338,31339,31557,31666,31745,31780,31785,31787,31788,31789,31790,31791,31792,32000,\
        32001,32100,32222,32418,32768,32770,32771,32772,32773,32774,32775,32776,32777,32778,32779,32780,32786,32787,32791,33000,33270,\
        33333,33390,33567,33568,33577,33777,33911,34000,34324,34444,34555,35000,35555,36000,36666,37000,37237,37266,37651,37777,38000,\
        38741,38888,39000,39507,39999,40000,40412,40421,40422,40423,40424,40425,40426,41000,41111,41337,41666,42000,42222,43000,43188,\
        43210,43333,44000,44442,44443,44444,44575,44767,45000,45555,45559,45673,46000,46666,47000,47017,47252,47262,47557,47777,48000,\
        48001,48002,48003,48004,48005,48006,48888,49000,49301,49999,50000,50130,50505,50766,50776,51000,51111,51966,52000,52222,52317,\
        53000,53001,53333,54000,54283,54320,54321,54444,55000,55165,55166,55555,56000,56666,57000,57341,57777,58000,58339,58888,59000,\
        59999,60000,60001,60008,60068,60411,61000,61111,61348,61439,61440,61441,61466,61603,62000,62222,62452,62453,62454,62455,62456,\
        62457,62458,63000,63333,63485,63884,63885,63886,63887,63888,63889,64000,64101,64444,65000,65301,65390,65421,65432,65530,65531,\
        65532,65533,65534,65535"

    if ( typeofports == "full"):
        return_ports == "1-65535"
    PlusPrint ('','')

    return return_ports
#   ---- end of getports

#@(#) ----------------------------------------------------------------
#@(@) funtion name: gencsv
#@(#) input:filename
#@(#) return:
#@(#) What: generates a csv file based upon the tcp and ping xml file
#@(#)
def gencsv(infilename):
    PlusPrint ('File name', infilename)
    tcpxmlfile = infilename+".tcp.xml"
    pngxmlfile = infilename+".ping.xml"
    csvfile = infilename+".csv"
    portid = []
    uniqueportlist =[]
    scandict = {}

    pingxml = NmapParser.parse_fromfile(pngxmlfile)
    pinghost={}
    ep={}
    for _host in pingxml.hosts:
        if _host.is_up():
            isup="11"
        else:
            isup="12"
        pinghost[_host.address]=isup
        # + ---
        # + debug print the ping status
        #for k,v in pinghost.items():
        #    print (k, v)

    rep = NmapParser.parse_fromfile(tcpxmlfile )
    # print ("Address,Ports"
    for _host in rep.hosts:
        if (_host.extraports_state['state']['state']) == 'filtered':
            ep[_host.address]='3'
        elif (_host.extraports_state['state']['state']) == 'closed':
            ep[_host.address]='2'
        elif (_host.extraports_state['state']['state']) == 'open':
            ep[_host.address]='1'
        else:
            ep[_host.address]='0'
        # ep[_host.address]=(_host.extraports_state['state']['state'])
        templist = [x[0] for x in _host.get_ports()]
        for i in templist:
            portid.append( i )
            # print ("Reason:" , _host.reason(i) )

    uniqueportlist = sorted(list(set(portid)))
    for _host in rep.hosts:
    # - looping over all host
        if _host.is_up() and len(_host.get_ports()) != 0:
        # if host is up and number of ports is >0
            tempdict = {}
            # we put all services into
            for serv in _host.services:
                tempdict[serv.port] = serv.state
            null = None
            tlist =[]
            for p in uniqueportlist:
                if p in tempdict:
                    if tempdict.get(p) == 'open':
                        tlist.append("1")
                    elif tempdict.get(p) == 'closed':
                        tlist.append("2")
                    elif tempdict.get(p) == 'filtered':
                        tlist.append("3")
                else:
                    tlist.append('')
            # print (_host.address,',', str(tlist).strip('[]'))
            scandict[str(IPAddress(_host.address))] = tlist
            #scandict[int(IPAddress(_host.address))] = tlist

        # processing scandata ready for reports.
        # sorting the IP nummerically
        keys = scandict.keys()
#
#  need to add ping and filtered into the headding
#
        headding = str(uniqueportlist).strip('[]')
        h ="Host,Ping,Ext ports,"
        #with open(options.csvfil, 'w', encoding='UTF8', newline='') as f:
        with open(csvfile, 'w', encoding='UTF8', newline='') as f:
            f.write(h+headding + "\n" )
            # print (h+headding )
            for each in keys:
                listrow = str(scandict.get(each)).strip("'[]'")
                listrow = listrow.replace('\'','')
                # print (str(IPAddress(each)) + "," + pinghost[each] +"," + ep[each] + ","+ listrow + "\n" )
                f.write(str(IPAddress(each)) +","+pinghost[each]+"," +  ep[each] + ","+ listrow + "\n" )
        f.close()
    return
#@(#) + end gencsv

#@(#) ----------------------------------------------------------------
#@(@) funtion name: stripBadChars
#@(#) input:filename
#@(#) return: a safe filename
#@(#) What: Strips a string for bad chars for a filename
#@(#)
def stripBadChars(filename):
    # strips away bad chars from filename
    keepcharacters = ('.','_','-')
    MinusPrint ('Removing bad chars in ' , filename)
    filename = re.sub(r"\s+", '_', filename)
    MinusPrint ('Files are located in: ' , filename)
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

#@(#) ----------------------------------------------------------------
#@(@) funtion name: findOpenPorts
#@(#) input: project name, xml file, file for open ports
#@(#) return: none
#@(#) What: finds open ports and adds to file
#@(#)
def findOpenPorts(c, discoverxml,openports):
    PlusPrint("  finding open ports for: " , c)
    outf = open(openports,'w')
    xmldoc = minidom.parse(discoverxml)

    pid=[]
    reslist=[]

    portlist = xmldoc.getElementsByTagName('port')
    nrport = len(portlist)
#<port protocol="tcp" portid="135"><state state="closed" reason="reset" reason_ttl="64"/><service name="msrpc" method="table" conf="3"/></port>

    for port in portlist:
       state = port.getElementsByTagName('state')
       for port in portlist:
           state = port.getElementsByTagName('state')
           # if  port.attributes['protocol'].value == 'tcp':
           for i in state:
               if  i.attributes['state'].value == "open":
                   # print i.attributes['state'].value
                   pid.append( port.attributes['portid'].value )

    reslist = sorted(sorted(set(pid)), key=int)

    nropenports = len(reslist)
    PlusPrint ( "antall unike porter:", str(nropenports) )
    tx =  ','.join(str(x) for x in reslist)
    outf.write(tx)
    outf.close()
    #print tx
    return (nropenports)


#@(#) ----------------------------------------------------------------
#@(@) funtion name: findlivehosts
#@(#) input:project name, xml file, fil for livehosts
#@(#) return: none
#@(#) What: find all hosts which are alive
#@(#)
def findlivehosts(c, discoverxml,livehosts):
    # Parser ping.xml filen.
    PlusPrint("  finding live host for: " , c)
    outf = open(livehosts,'w')

    f = discoverxml
    xmldoc = minidom.parse(discoverxml)
    hostlist = xmldoc.getElementsByTagName('host')
    nrhost = len(hostlist)

    PlusPrint ("  found : " , str(nrhost) + " live hosts")
    s = 0
    templist=[]
    for host in hostlist:
        s += 1
        # print "nr. ", s,
        status = host.getElementsByTagName('status')
        for i in status:
            # print  i.attributes['state'].value,
            if  i.attributes['state'].value == "up":
                ip = host.getElementsByTagName('address')
                for t in ip:
                    #if ( options.debug ):
                    if re.findall( r'[0-9]+(?:\.[0-9]+){3}', t.attributes['addr'].value ):
                        templist.append(t.attributes['addr'].value)
                        # MinusPrint(  ' fond ip' , t.attributes['addr'].value + " ")
                    # regex too find MAC adresses :-)
                    # if  re.match( "[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", t.attributes['addr'].value.lower()):
                    # else:
    tx =  ' '.join(str(x) for x in templist)
    outf.write(tx)
    outf.close()
    return nrhost
#   ---- end of findLivehosts

#@(#) ----------------------------------------------------------------
#@(@) funtion name: getHostNameIP
#@(#) input: none
#@(#) return: hostname and IP
#@(#) What:
#@(#)
def getHostNameIP():
    hn=""
    ip=""
    try:
        host_name = socket.gethostname()
        hn = host_name.split('.')[0]
        ip = socket.gethostbyname(host_name)
    except:
        if hn == "":
            hn="unknown"
        if ip == "":
            ip="unknown"
        # print("Unable toget Hostname and IP")
    return (hn,ip)
#   ---- end of getHostNameIP

#@(#) ----------------------------------------------------------------
#@(@) funtion name: runWebHook
#@(#) input: Customer name and a Webhook
#@(#) return: none
#@(#) What: sends a teams msg
#@(#)
def runWebHook(lcust, lwebhook,lports,lhosts,ltt ):
    #
    today = datetime.datetime.now().strftime('%Y %m %d %H:%M')
    lwebhook = lwebhook.rstrip('\t\n\r')
    ltt = ltt + " [s]"
    hn=""
    ip=""
    if lports:
        openports=lports
    else:
        openports=0
    if lhosts:
        livehosts=lhosts
    else:
        livehosts=0
    (hn,ip) = getHostNameIP()
    title="Nmap scan ("+program + ") results"
    try:

        myTeamsMessage = pymsteams.connectorcard(lwebhook)
        myMessageSection = pymsteams.cardsection()
        #myTeamsMessage.title("Nmap scan ("+program + ") results")
        myTeamsMessage.title(title)
        myTeamsMessage.text(" " )

        myMessageSection.addFact("Hostname:", hn)
        myMessageSection.addFact("IP address:", ip)
        myMessageSection.addFact("Run time:", ltt )
        myMessageSection.addFact("Finished at:", today )
    #
        Section1 = pymsteams.cardsection()
        Section1.text("Project information:")
        Section1.addFact("Project Name:", lcust)
        Section1.addFact("# of live hosts:", livehosts)
        Section1.addFact("# of open ports:", openports)

        # # Add both Sections to the main card object
        myTeamsMessage.addSection(Section1)
        myTeamsMessage.addSection(myMessageSection)
        #myTeamsMessage.printme()
        myTeamsMessage.send()
    except Exception as e:
            raise RuntimeError("MS Teams: ERROR - %s", e)
    return

#   ---- end of runWebHook

#@(#) ----------------------------------------------------------------
#@(@) funtion name: checkwebhook
#@(#) input: none
#@(#) return: a webhook URL
#@(#) What: reads webhook from the file:
#@(#) /opt/werfen/cfg/nmapMSteam.hook.txt
def checkwebhook():
    wh=""
    webhook="/opt/werfen/cfg/nmapMSteam.hook.txt"
    if os.path.isfile(webhook):
        with open(webhook, 'r') as f:
            line = f.readlines()
            for i in line:
                i = i.rstrip('\r\n\t')
                wh=i.split('=')[1]
            if not is_valid_url(wh):
                wh=""
    return (wh)

#   ---- end of checkwebhook
#@(#) ----------------------------------------------------------------
#@(@) funtion name: DoScan
#@(#) input:
#@(#) return: none
#@(#) What: runs nmap with parameters given and filename for storeing result
#@(#)
def DoScan(tos, dstfile, widenmap, b):
    dailylogfile = open(b, 'a')

    Doscanstart = time.time()
    PlusPrint (' Running ' + tos + ' scan: ' , widenmap )
    # runnmap = subprocess.Popen([widenmap], shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    runnmap = subprocess.Popen([widenmap], shell=True,stdout=dailylogfile, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    # runnmap = subprocess.Popen([widenmap], stdout=dailylogfile, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    for line in runnmap.stderr:
        sys.stdout.write(str(line))
        sys.stdout.flush()
        dailylogfile.write(str(line) )
    runnmap.wait()
    stdout, stderr = runnmap.communicate()
    doscanstop = time.time()
    totaldoscan = doscanstop - Doscanstart
    totaldoscan = ( "%.2F" % totaldoscan )
    PlusPrint ('  elapsed ' + tos + ' time: ' , str(totaldoscan) + ' [s]')

# + ------------------------------------------------------------------------------- + #
# + checking input parameters
# + ------------------------------------------------------------------------------- + #
if ( ccustomer is None or options.ip is None or options.port is None ):
    parser.print_help()
    if ( options.debug ):
        PlusPrint('Options are:' , str(options))
        PlusPrint('Arguments are:' , str(args))
    sys.exit()


# + ------------------------------------------------------------------------------- + #
# + adjusting the different OSes
# + ------------------------------------------------------------------------------- + #
OS = sys.platform
if OS == 'darwin'.lower():
    if ( options.debug ):
        PlusPrint ('Running on correct OS: ' , OS )
    nmap = "/opt/homebrew/bin/nmap"
    rsync="/usr/bin/rsync"
    if not os.path.exists(nmap):
        PlusPrint ('  wakey, wakey\n \t is nmap installed here !!:' , nmap )
        sys.exit()

elif OS == 'Linux'.lower():
    if ( options.debug ):
        PlusPrint ('Running on the second best OS: ' , OS)
    nmap = "/usr/bin/nmap"
    rsync="/usr/bin/rsync"
    if not os.path.exists(nmap):
        PlusPrint (' - wakey, wakey\n \t is nmap installed here !!:' , nmap  )
        sys.exit()
elif OS == 'Windows':
    if ( options.debug ):
        PluaPrint ('Really sure what you are doing ...', ':-)' )
else:
    PlusPrint ('I do not know how to handle you...' , ':-|' )
    sys.exit()

# setting default timeout unless it is set
if options.defaulttimeout is None:
    if ( options.debug):
        MinusPrint('  setting default time out=', '50ms')
    defaulttimeout = "50ms"
else:
    if ( options.debug):
        MinusPrint('  setting default time out=', options.defaulttimeout)
    defaulttimeout = options.defaulttimeout + "ms"
            #if type(n) is int


#@(#) ----------------------------------------------------------------
#@(@) funtion name: main
#@(#) input: sys.argv
#@(#) return:
#@(#) What:
#@(#)
def main(argv):
    #(@) + ----------------------------------------------------------
    #(@) + validate user access rights.
    #(@) + ----------------------------------------------------------
    # Function: check runtime user

    PlusPrint  (" Program " ,"'"+ program + "' start")
    if ((( os.getenv("USER") == "root" ) or (os.getenv("LOGNAME") == "root"))  and (str ( os.getenv("SUDO_USER"))  != "None")):
        MinusPrint (' Hello ', str(os.getenv("SUDO_USER")) )
        MinusPrint (' you are running as ' , str(os.getenv("USER")) )
    elif ((( os.getenv("USER") == "root" ) or (os.getenv("LOGNAME") == "root")) and (str ( os.getenv("SUDO_USER"))  == "None")):
        MinusPrint (' Hello ' , str(os.getenv("USER")) )
        MinusPrint (' ', 'Who ever you are ...')
    else:
        PlusPrint (" You do not have enought access rigths to run: ", program  )
        PlusPrint (os.getenv())
        sys.exit()

    #(@) + ----------------------------------------------------------
    #(@) + checking web-hook config
    #(@) + ----------------------------------------------------------
    webhook = checkwebhook()

    creatDir("/export")

    #(@) + ----------------------------------------------------------
    #(@) + Input validation
    #(@) + ----------------------------------------------------------
    if not options.customer:
        PlusPrint("Option -c project name is"," Mandatory!" )
        sys.exit(1)
    ccustomer = stripBadChars( options.customer )
    if not CheckPath (WideAngle + "/" + ccustomer):
        pass
        PlusPrint(' Program exiting...',' environment not correct!')

    else:
        # discoverscan :
        try:
            datentime = strftime("%Y%m%dT%H%M%S")
            dd = strftime("%Y%m%d") + "." + ccustomer + ".log"
            discoverports = getports("discover")
            if options.port == "F":
                destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"full"+ ".ping"
            elif options.port =="N":
                destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"normal"+ ".ping"
            else:
                destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"part"+ ".ping"

            tmpfile = destinationfile
            lvh  = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"livehosts.txt"
            dailylog  = WideAngle + "/" + ccustomer + "/" + dd

    #(@) + ----------------------------------------------------------
    #(@) + Building nmap command line string
    #(@) + ----------------------------------------------------------
            wideangle = nmap + " -sn -n -PE --max-hostgroup 150 --max-retries 4 --min-rtt-timeout 100ms --initial-rtt-timeout 500ms --scan-delay 2ms --max-scan-delay 20ms --min-rate 450 --max-rate 15000 --max-rtt-timeout " + defaulttimeout + " " + discoverports + " -oA "  + destinationfile + " "+ options.ip
            DoScan("discover", destinationfile, wideangle, dailylog )
            numberoflivehost = findlivehosts(ccustomer, destinationfile+".xml", lvh)

            # quick scan
            # system("nmap -A -T4 --min-rate 75 -Pn --defeat-rst-ratelimit --max-scan-delay 0 -F -v -oA $fast_out -iL $live_hosts_file -n --max-hostgroup 150 --max-rtt-timeout 50ms");
            # ----
            discoverports = getports("quick")
            destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"quick"
            if numberoflivehost == 0 or bool(options.Pnull) == True :
                # no alive host? lets quick scan them all
                PlusPrint ("  Scanning ALL host: " , str(options.Pnull) )
                outf = open(lvh,'w')
                outf.write(options.ip)
                outf.close()
            wideangle = nmap + " -sS -A -T4 --min-rate 71 -Pn --defeat-rst-ratelimit --max-scan-delay 0 -F -v  -oA "  + destinationfile + " -iL " + lvh + " -n --max-hostgroup 150 --max-rtt-timeout " + defaulttimeout
            DoScan("quick", destinationfile, wideangle, dailylog)

            # tcp scan with given input ports
            #
            # ----
            PlusPrint('  time for heavy ',  'duty nmap scaning')

            if options.port == "F":
                MinusPrint (' FULL nmap scan', ' 65535 + ports')
                destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"full"+".tcp"
                wideangle = nmap + " -A -T4 --min-rate 75 -Pn --defeat-rst-ratelimit --max-scan-delay 0 -sS -v -oA " + destinationfile + " -n --max-hostgroup 150 --max-rtt-timeout 50ms -p 1-65535" + " -iL " + lvh
                discoverports = getports("full")
                DoScan("full", destinationfile, wideangle, dailylog)
                # copy ping.xml file to full.ping.xml
                # Eureka requirement
                # subprocess.Popen(['cp '  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            elif options.port == "N":
                MinusPrint (' Normal nmap scan', ' 4000 + ports')
                discoverports = getports("normal")
                destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"normal"+".tcp"
                wideangle = nmap + " -A -T4 --min-rate 75 -Pn --defeat-rst-ratelimit --max-scan-delay 0 -sS -v -oA " + destinationfile + " -n --max-hostgroup 150 --max-rtt-timeout 50ms -p  " + discoverports + " -iL " + lvh
                DoScan("normal", destinationfile, wideangle, dailylog)

            else:
                print ( "options.port: " + options.port)
                MinusPrint (' Custom scan of ', options.port)
                destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"part"+".tcp"
                wideangle = nmap + " -A -T4 --min-rate 75 -Pn --defeat-rst-ratelimit --max-scan-delay 0 -sS -v -oA " + destinationfile + " -n --max-hostgroup 150 --max-rtt-timeout 50ms -p \" " + options.port +  "\"  -iL " + lvh
                # discoverports = getports("normal")
                DoScan("custom", destinationfile, wideangle, dailylog)
                # MinusPrint (' Do not know how to hadle: ' , options.port )
            #
            # Doing som accounting
            # ----
            # generating CSV file until DB is in place.
            csvfiletemp=destinationfile[:-4]
            gencsv(csvfiletemp)
            # finding alive #host and open #ports
            #
            xfile  = destinationfile + ".xml"
            openp  = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"openports.txt"
            numberofopenports = findOpenPorts(ccustomer, xfile, openp)


            # finally UDP scan
            #
            # ----
            if (options.udp):
                PlusPrint('  starting UDP scan', ' ' )
                destinationfile = WideAngle + "/" + ccustomer + "/" + ccustomer+"."+datentime+"."+"udp"
                wideangle = nmap + " -A -T4 --min-rate 75 -Pn --max-scan-delay 0 -sU -v -oA " + destinationfile + " -n --max-hostgroup 150 --max-rtt-timeout 50ms  -iL " + lvh + " -p " + discoverports
                DoScan("udp", destinationfile, wideangle, dailylog)
            #system("nmap -A -T4 --min-rate 75 -Pn --max-scan-delay 0 -sU -v -oA $udp_out -iL $live_hosts_file -n --max_hostgroup 150 --max-rtt-timeout 50ms");

            #
            # cleanup
            #  rsync xml files to /export/nmap catalog
            src = WideAngle  + "/" + ccustomer + "/*.xml "
            wideangle = rsync + " -az --compress " + src + " /export/nmapxml "
            DoScan("cleanup", " ", wideangle, dailylog)

        except (KeyboardInterrupt, SystemExit):
            PlusPrint ("\n ... Outch! Interrupt caught ", "-rolling back what ever. Gracefully exiting ...")
            sys.exit()
    ten = time.time()
    timetotal = ten - tnull
    timetotal = ("%.2f" % timetotal )
    PlusPrint  ( ' ' +program , ' runtime ' + str(timetotal) + ' [s]')
    PlusPrint  ("- Program '" + program , "' stop")
    # + -------
    # + Last thing we do, send a msg if you want one
    # +
    if (options.alert and webhook):
        PlusPrint("Running runWebHook",ccustomer)
        runWebHook(ccustomer, webhook,numberofopenports,numberoflivehost, timetotal)

if __name__ == "__main__":
    main(sys.argv)

