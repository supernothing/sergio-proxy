#!/usr/bin/env python
'''
A module that provides various useful functions for interacting
with IP addresses.
'''

import re
import socket

__author__ = "Ben Schmidt"
__copyright__ = "Copyright 2010, Ben Schmidt"
__credits__ = ["Ben Schmidt"]
__license__ = "GPL v3"
__version__ = "0.2"
__maintainer__ = "Ben Schmidt"
__email__ = "supernothing@spareclockcycles.org"
__status__ = "beta"

#My nasty, way too long regexes. Any tips from regex masters here would be appreciated
match_cidr = re.compile("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[/](3[012]|[0-2]?[0-9])$")
match_hyphen = re.compile("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(-(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))?\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(-(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))?$")
#This isn't working, but hyphen still is o.O hacked around to fix for now
#match_ip = re.compile("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\$")

def is_ip(ip):
    '''Checks for valid IP address'''
#    if match_ip.match(ip)!=None: return True
#    else: return False
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False
def is_cidr_range(ip):
    '''Checks for valid CIDR range'''
    if match_cidr.match(ip)!=None: return True
    else: return False
def is_hyphenated_range(ip):
    '''Checks for valid hyphenated range'''
    if match_hyphen.match(ip)!=None: return True
    else: return False

def ip_to_num(ip):
    '''Takes an IP string and returns its decimal equivalent'''
    octects = ip.split(".")
    if len(octects) == 4:
        num = sum([int(octects[i])<<((3-i)*8) for i in range(0,4)])
        if num < 0 or num > 0xFFFFFFFF: return None
        else: return num
    else:
        return None

def num_to_ip(num):
    '''Takes an decimal representation of an IP and converts to a string'''
    if num < 0 or num > 0xFFFFFFFF: return None
    else: return ".".join([str((num>>((3-i)*8))&0xFF) for i in range(0,4)])

def get_range_ips(iprange):
    '''Given an IP range string in CIDR or hyphenated notation,
    this function will return the start and end IPs, in string
    form, in an ordered tuple'''
    if is_cidr_range(iprange):
    #CIDR notation
        start,cidr = iprange.split("/")
        start_num,cidr_num = ip_to_num(start),2**(32-int(cidr))-1
        end_num = start_num|cidr_num
        start_num = end_num&(0xFFFFFFFF<<(32-int(cidr)))
        return num_to_ip(start_num),num_to_ip(end_num)
    elif is_ip(iprange):
        #single IP - must be before hyphenated notation check
        return iprange,iprange
    elif is_hyphenated_range(iprange):
    #Hyphenated notation
        start,end = [],[]
        for octect in iprange.split("."):
            octect = octect.split("-")
            if len(octect)==2: i = 1
            else: i = 0
            start.append(octect[0])
            end.append(octect[i])
        return ".".join(start),".".join(end)
    else:
    #Not supported range
        print "Supplied IP format not supported."
        raise TypeError

def range_gen(start,end):
    for ip in xrange(ip_to_num(start),ip_to_num(end)+1):
        yield num_to_ip(ip)
