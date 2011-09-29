#!/usr/bin/env python
"""Sergio Proxy is a MITM tool based on Moxie Marlinspikes's sslstrip"""

__author__ = "Ben Schmidt"
__email__  = "supernothing@spareclockcycles.org"
__license__= """
Copyright (c) 2010-2011 Ben Schmidt <supernothing@spareclockcycles.org>
 
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA

"""
from twisted.web import http
from twisted.internet import reactor

from sslstrip.StrippingProxy import StrippingProxy
from sslstrip.URLMonitor import URLMonitor
from sslstrip.CookieCleaner import CookieCleaner
from sslstrip.ProxyPlugins import ProxyPlugins

import sys, logging, traceback, string, os
import argparse


from plugins import *
plugin_classes = plugin.Plugin.__subclasses__()

sslstrip_version = "0.9"
sergio_version = "0.2"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
           description="Sergio Proxy v%s - An HTTP MITM Tool" % sergio_version,
           epilog="Use wisely, young Padawan.",
           fromfile_prefix_chars='@' )
    #add sslstrip options
    sgroup = parser.add_argument_group("sslstrip",
           "Options for sslstrip library")

    sgroup.add_argument("-w","--write",type=argparse.FileType('w'),
           metavar="filename", default=sys.stdout,
           help="Specify file to log to (stdout by default).")
    sgroup.add_argument("--log-level",type=str,
           choices=['debug','info','warning','error'],default="info",
           help="Specify file to log to (stdout by default).")
    slogopts = sgroup.add_mutually_exclusive_group()   
    slogopts.add_argument("-p","--post",action="store_true",
           help="Log only SSL POSTs. (default)")
    slogopts.add_argument("-s","--ssl",action="store_true",
           help="Log all SSL traffic to and from server.")
    slogopts.add_argument("-a","--all",action="store_true",
           help="Log all SSL and HTTP traffic to and from server.")
    sgroup.add_argument("-l","--listen",type=int,metavar="port",default=10000,
           help="Port to listen on (default 10000)")
    sgroup.add_argument("-f","--favicon",action="store_true",
            help="Substitute a lock favicon on secure requests.")
    sgroup.add_argument("-k","--killsessions",action="store_true",
            help="Kill sessions in progress.")
   
    #add msf options
    sgroup = parser.add_argument_group("MSF",
            "Generic Options for MSF integration")

    sgroup.add_argument("--msf-path",type=str,default="/pentest/exploits/framework3/",
            help="Path to msf (default: /pentest/exploits/framework3)")

    #Initialize plugins
    plugins = []
    try:
        for p in plugin_classes:
            plugins.append(p())
    except:
        print "Failed to load plugin class %s" % str(p)

    #Give subgroup to each plugin with options
    try:
        for p in plugins:
            if p.desc == "":
                sgroup = parser.add_argument_group("%s" % p.name,
                    "Options for %s." % p.name)
            else:
                sgroup = parser.add_argument_group("%s" % p.name,
                    p.desc)
                
            sgroup.add_argument("--%s" % p.optname, action="store_true",
                    help="Load plugin %s" % p.name)
            if p.has_opts:
                p.add_options(sgroup)
    except NotImplementedError:
        print "Plugin %s claimed option support, but didn't have it." % p.name

    args = parser.parse_args()
    args.full_path = os.path.dirname(os.path.abspath(__file__))
    
    log_level = logging.__dict__[args.log_level.upper()]
    
    #Start logging 
    logging.basicConfig(level=log_level, format='%(asctime)s %(message)s',
                        stream=args.write)
    
    #All our options should be loaded now, pass them onto plugins
    load = []
    try:
        for p in plugins:
            if  getattr(args,p.optname):
                p.initialize(args)
                load.append(p)
    except NotImplementedError:
        print "Plugin %s lacked initialize function." % p.name

    #Plugins are ready to go, start MITM
    URLMonitor.getInstance().setFaviconSpoofing(args.favicon)
    CookieCleaner.getInstance().setEnabled(args.killsessions)
    ProxyPlugins.getInstance().setPlugins(load)

    strippingFactory              = http.HTTPFactory(timeout=10)
    strippingFactory.protocol     = StrippingProxy

    reactor.listenTCP(args.listen, strippingFactory)
    
    print "\nsslstrip " + sslstrip_version + " by Moxie Marlinspike running..."
    print "sergio-proxy v%s online" % sergio_version
    
    reactor.run()
    
    #cleanup on exit
    for p in load:
        p.finish()
