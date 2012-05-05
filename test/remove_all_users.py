#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 


import pymongo

if __name__ == "__main__":
        c = pymongo.Connection("localhost", 27017) #This is default
        c.blog.users.remove()
        print("all users removed!")


# vim: ai ts=8 sts=8 et sw=8
