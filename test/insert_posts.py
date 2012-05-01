#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 

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
        insert_many_posts(posts, p1)



# vim: ai ts=8 sts=8 et sw=8
