#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 

from __future__ import print_function
import pymongo
import time

def insert_many_posts(posts ,p1)
        for i in range(100):
                post = {"title": p1["title"], "markdown" : p1["markdown"], "html" : p1["html"], "time" : int(time.time()), "author": p1["author"]}
                posts.insert(post)


if __name__ == "__main__":
        c = pymongo.Connection("localhost", 27017)
        posts = c.blog.posts
        p1 = posts.find_one()
        if p1:
                insert_many_posts(posts, p1)
        else:
                print("There's no posts now, please at least have one post in database.")



# vim: ai ts=8 sts=8 et sw=8
