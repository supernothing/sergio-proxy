#!/usr/bin/env python
'''
An implementation of a transparent proxy using the Twisted
networking framework for Python.

For usage help, see example UserMITM.py and start_server.py 
provided in this package.

Copyright 2010, Ben Schmidt
Released under the GPLv3
'''
import types,gzip
from cStringIO import StringIO
from twisted.internet import reactor
import urlparse


from twisted.web import proxy
from MITM import MITM


__author__ = "Ben Schmidt"
__copyright__ = "Copyright 2010, Ben Schmidt"
__credits__ = ["Ben Schmidt"]
__license__ = "GPL v3"
__version__ = "0.1"
__maintainer__ = "Ben Schmidt"
__email__ = "supernothing@spareclockcycles.org"
__status__ = "alpha"

mitm = MITM([],[])
print "Imported Request Functions:",", ".join([a.__name__ for a in mitm.req_funcs])
print "Imported Reply Functions:",", ".join([a.__name__ for a in mitm.reply_funcs])

class TransparentProxyClient(proxy.ProxyClient):
    """
    Used by TransparentProxyClientFactory to implement an transparent web proxy.
    """

    def __init__(self, command, rest, version, headers, data, father):
        self.buffer,self.data=StringIO(),StringIO()
        self.response_headers,self.rh_list = {},[]
        proxy.ProxyClient.__init__(self, command, rest, version, headers, data, father)
        
    def uses_gzip(self):
        if "Content-Encoding" in self.response_headers and self.response_headers["Content-Encoding"].find("gzip")!=-1: return True
        else: return False
        
    def handleStatus(self, version, code, message):
        if message:
            message = " %s" % (message,)
        self.message = "%s %s%s\r\n" % (version, code, message)
        
    def handleHeader(self, key, value):
        self.response_headers[key]=value
        self.rh_list.append(key)
        
    def handleEndHeaders(self):
        pass
    
    def handleResponsePart(self,buffer):
        self.buffer.write(buffer)
        
    def handleResponseEnd(self):
        #Handle gzip compression if present
        self.buffer.seek(0)
        if self.uses_gzip():
            self.data = gzip.GzipFile(fileobj=self.buffer).read()
        else:
            self.data = self.buffer.getvalue()
        #Mess with the data however we want :)
        mitm.process_reply(self)
        #Need to recompress and update content length to make everyone happy
        out_data = StringIO()
        if self.uses_gzip():
            gzip.GzipFile(mode='wb',fileobj=out_data).write(self.data)
        else:
            out_data.write(self.data)
        self.response_headers['Content-Length']=str(len(out_data.getvalue()))
        if "message" in self.__dict__:
            self.father.transport.write(self.message)
        for i in self.rh_list: self.father.transport.write("%s: %s\r\n" % (i,self.response_headers[i]))
        self.father.transport.write("\r\n")
        self.father.transport.write(out_data.getvalue())
        if out_data.getvalue().find("HTTP/1.1") != -1: print "OMG WTF"
        proxy.ProxyClient.handleResponseEnd(self)
        
class TransparentProxyClientFactory(proxy.ProxyClientFactory):
    """
    Used by ProxyRequest to implement an transparent web proxy.
    """

    protocol = TransparentProxyClient

class TransparentProxyRequest(proxy.ProxyRequest):
    """
    Used by TransparentProxy to implement an transparent web proxy.
    """
    protocols = {'http': TransparentProxyClientFactory}
    def __init__(self, channel, queued, reactor=reactor):
        proxy.ProxyRequest.__init__(self, channel, queued,reactor)
    def process(self):
        #print dir(self)f)
        #This is here in case we need it later
        parsed = list(urlparse.urlparse(self.uri))
        if parsed[0]=="":
            parsed[0]="http"
        if parsed[1]=="" and 'host' in self.getAllHeaders():
            parsed[1]=self.getAllHeaders()['host']
        else:
            parsed[1]=self.host.host
        self.uri = urlparse.urlunparse(parsed)
        mitm.process_request(self)
        proxy.ProxyRequest.process(self)

class TransparentProxy(proxy.Proxy):
    """
    This class implements a simple transparent web proxy.
    """

    requestFactory = TransparentProxyRequest
