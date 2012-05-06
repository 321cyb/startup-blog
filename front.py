#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 

class Post():
        post_id = ""
        title = ""
        mtime = 0 #last modify timestamp
        ctime = 0 #create timestamp
        author = ""
        markdown = ""
        html = ""

        def __init__(self, post_id, title, author, mtime, ctime, markdown = "", html = ""):
                self.post_id = post_id
                self.title = title
                self.author = author
                self.mtime = mtime
                self.ctime = ctime
                self.markdown = markdown
                self.html = html


class User():
        name = "" #This is what showes on the web page 
        provider = "" #"douban" or "weibo", "" means local site.
        #This associates with provider, and this should not change when name changes.
        #For local user, uid should equal to name.
        uid = "" 
        email = ""
        qq = ""
        gtalk = ""

        def __init__(self,  name = "", provider = "", uid = "", email = "", qq = "", gtalk = ""):
                self.name = name
                self.provider = provider
                self.uid = uid
                self.email = email
                self.qq = qq
                self.gtalk = gtalk





# vim: ai ts=8 sts=8 et sw=8
