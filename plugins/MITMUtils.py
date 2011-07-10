import re

def insert_html(req,data,pre=[],post=[],re_flags=re.I):
    '''
    To use this function, simply pass a list of tuples of the form:
    
    (string/regex_to_match,html_to_inject)
    
    NOTE: Matching will be case insensitive unless differnt flags are given
    
    The pre array will have the match in front of your injected code, the post
    will put the match behind it.
    '''
    pre_regexes = [re.compile(r"(?P<match>"+i[0]+")",re_flags) for i in pre]
    post_regexes = [re.compile(r"(?P<match>"+i[0]+")",re_flags) for i in post]
        
    if is_html(req):
        for i,r in enumerate(pre_regexes):
            data=re.sub(r,"\g<match>"+pre[i][1],data)
        for i,r in enumerate(post_regexes):
            data=re.sub(r,post[i][1]+"\g<match>",data)
    return data

def check_mimetype(req,t):
    return 'Content-Type' in req.headers and\
        req.headers['Content-Type'].find(t)!=-1

def is_html(req):
    '''Check if MIME type indicates an HTML file'''
    return check_mimetype(req,"text/html")
