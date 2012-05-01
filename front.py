#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 

class Post():
        post_id = ""
        title = ""
        mtime = 0 #timestamp
        author = ""
        markdown = ""
        html = ""

        def __init__(self, post_id, title, author, mtime, markdown = "", html = ""):
                self.post_id = post_id
                self.title = title
                self.author = author
                self.mtime = mtime
                self.markdown = markdown
                self.html = html


class User():
        name = ""
        email = ""
        qq = ""
        gtalk = ""

        def __init__(self, name, email = "", qq = "", gtalk = ""):
                self.name = name
                self.email = email
                self.qq = qq
                self.gtalk = gtalk





# vim: ai ts=8 sts=8 et sw=8
