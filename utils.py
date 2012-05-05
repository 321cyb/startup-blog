#!/usr/bin/env  python3
#-*- coding: utf-8 -*-
#Author: Kevin Chen
#Date: 


def provider_and_uid(user):
        if user.startswith("weibo\x00"):
                return {"provider": "weibo", "uid": user.replace("weibo\x00", "")}
        elif user.startswith("renren\x00"):
                return {"provider": "renren", "uid": user.replace("renren\x00", "")}
        elif user.startswith("douban\x00"):
                return {"provider": "douban", "uid": user.replace("douban\x00", "")}
        else:
                return {"provider": "", "uid": user} # This is local user.






# vim: ai ts=8 sts=8 et sw=8
