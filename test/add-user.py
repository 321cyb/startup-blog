#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 


import pymongo
import sys
import os
import hashlib


if __name__ == "__main__":
        if len(sys.argv) != 3:
                print("usage: {0} user password".format(sys.argv[0]))
        else:
                user = sys.argv[1]
                passwd = sys.argv[2]
                c = pymongo.Connection("localhost", 27017) #This is default
                salt = os.urandom(8)
                password = hashlib.sha256(passwd.encode() + salt).hexdigest()
                c.blog.users.insert({"name": user, "provider": "", "uid": user, "password": password, "salt": salt, "access_token": ""})

         






# vim: ai ts=8 sts=8 et sw=8
