#! /usr/bin/env python3
import sys, re



# --- ++++++++++++++++++++++++++++++++++++++++
#     Info: Check if input is valid CIDR
#     Return: True/False
# --- ++++++++++++++++++++++++++++++++++++++++
def is_cidr(ip):
#     pattern = re.compile(r"^((25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.){3}(25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)(/(3[012]|[12]\d|\d))?$")
    pattern = re.compile(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$")
    if pattern.search(ip):
        return ip is not None


# --- ++++++++++++++++++++++++++++++++++++++++
#     Info: Check if input is valid ipv4
#     Return: True/False
# --- ++++++++++++++++++++++++++++++++++++++++

def is_valid_ipv4(ip):
   pattern = re.compile(r"""
       ^
       (?:
         (?:
           # Decimal 1-255 (no leading 0's)
           [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
         )
         (?:                  # Repeat 0-3 times, separated by a dot
           \.
           (?:
             [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}|0
           )
         ){3}
       )
       $
   """, re.VERBOSE)
   return pattern.match(ip) is not None



# --- ++++++++++++++++++++++++++++++++++++++++
#     Info: Check if input is valid domain
#     Return: True/False
# --- ++++++++++++++++++++++++++++++++++++++++
def is_valid_domain(dom):
    regex = re.compile(r'^(?=.{4,255}$)([a-zA-Z0-9][a-zA-Z0-9-_]{,61}[a-zA-Z0-9]\.)+[a-zA-Z0-9]{2,5}$')
    regex2 = re.compile(r'^(?=.{4,255}$)([a-zA-Z0-9][a-zA-Z0-9-_]{,61}[a-zA-Z0-9]\.)+[a-zA-Z0-9]{2,5}\/.*$')
    if regex.search(dom):
        #return dom is not None and regex.search(dom)
        return dom is not None
    if regex2.search(dom):
        dom.split('/')[0]
        return dom is not None

# --- ++++++++++++++++++++++++++++++++++++++++
#     Info: Check if input is valid url
#     Return: True/False
# --- ++++++++++++++++++++++++++++++++++++++++
def is_valid_url(url):
    import re
    regex = re.compile(
        r'^h[xtXT]{2}ps?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-_]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

# --- ++++++++++++++++++++++++++++++++++++++++
#     Info: Check if input is valid MD5
#     Return: True/False
# --- ++++++++++++++++++++++++++++++++++++++++
def is_valid_md5(md5):
    import re
    regex = re.compile(
        r'^(?i)(?<![a-z0-9])[a-f0-9]{32}(?![a-z0-9])$', re.IGNORECASE)
    if regex.search(md5):
        return md5 is not None



def authenticate ():
    a=""
    b=""
    c=""
    d=""
    postgres_cfg = "/oa/cfg/dbhost.cfg"
    for n in (open(postgres_cfg).readlines()):
        ff = re.search(r'^dbhost=(.*)', n, re.M|re.I)
        if ff:
            a  = ff.group(1)
        ff = re.search(r'^inhouseDB=(.*)', n, re.M|re.I)
        if ff:
            b = ff.group(1)
        ff = re.search(r'^inhouseU=(.*)', n, re.M|re.I)
        if ff:
            c = ff.group(1)
        ff = re.search(r'^inhouseP=(.*)', n, re.M|re.I)
        if ff:
            d = ff.group(1)
    return ( a, b, c, d)



def main(argv):
    sys.exit()


if __name__ == "__main__":
    main(sys.argv)

