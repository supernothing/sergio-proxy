import logging
from cStringIO import StringIO

from plugins.plugin import Plugin
from MITMUtils import *

class Upsidedownternet(Plugin):
    name = "Upsidedownternet"
    optname = "upsidedownternet"
    has_opts = False
    implements = ["handleResponse","handleHeader"]
    def initialize(self,options):
        from PIL import Image,ImageFile
        globals()['Image'] = Image
        globals()['ImageFile'] = ImageFile
        self.options = options 
    def handleHeader(self,request,key,value):
        '''Kill the image skipping that's in place for speed reasons'''
        if request.isImageRequest:
            request.isImageRequest = False
            request.isImage = True
        else:
            request.isImage = False
    def handleResponse(self,request,data):
        if request.isImage:
            try:
                image_type=get_img_type(request)
                #For some reason more images get parsed using the parser
                #rather than a file...PIL still needs some work I guess
                p = ImageFile.Parser()
                p.feed(data)
                im = p.close()
                im=im.transpose(Image.ROTATE_180)
                output = StringIO()
                im.save(output,format=image_type)
                data=output.getvalue()
                open("/tmp/test.%s"%image_type,"w").write(output.getvalue())
                output.close()
            except Exception as e:
                print "EXCEPTION"
                print e
        return {'request':request,'data':data}
