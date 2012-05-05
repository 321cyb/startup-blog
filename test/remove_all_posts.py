#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 

from __future__ import print_function
import pymongo
import time


if __name__ == "__main__":
        c = pymongo.Connection("localhost", 27017)
        posts = c.blog.posts
        posts.remove()


# vim: ai ts=8 sts=8 et sw=8
