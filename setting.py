#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.getcwd(), "dependencies"))


#DO NOT CHANGE THIS! nginx forwards requests to here.
LISTEN_PORT = 8888


#DB setting
MONGODB_HOST = "localhost"
MONGODB_PORT =  27017


#cookie expries
COOKIE_EXPIRE_DAYS = 7

#How many posts to show on one page
POSTS_PER_PAGE = 2 


COOKIE_SECRET = b"KyjvoXg/TEuXSG9y4/6RmGxzFFYE1E/siECQTPBafAY="
