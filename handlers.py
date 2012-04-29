#!/usr/bin/env python

import tornado.web

import setting

import hashlib
import time
import datetime
import logging
import urllib.parse

import markdown
import pymongo

class BaseHandler(tornado.web.RequestHandler):
    def verifyuser(self, user, time):
        hit = self.application.db.users.find_one({"user": user})
        if hit:
            if datetime.datetime.now() - datetime.datetime.fromtimestamp(float(time))  < datetime.timedelta(days = setting.COOKIE_EXPIRE_DAYS):
                return True

        return False


class HomeHandler(BaseHandler):
    login_success = False
    user_status = "Not logged in."
    def get(self):
        if self.verifyuser(self.get_cookie("authenticated_user"), self.get_cookie("authenticated_time")):
            self.user_status = self.get_cookie("authenticated_user")
            self.login_success = True

        posts = self.application.db.posts.find().sort("time", pymongo.DESCENDING).limit(setting.POSTS_PER_PAGE)
        self.render("home.html", posts = posts)


class LoginHandler(BaseHandler):
    login_result = ""
    def get(self):
        login_failed = self.get_arguments("login_failed")
        if len(login_failed) > 0:
            self.login_result = "Login failed!"
            self.render("login.html" )
        else:
            self.render("login.html")

    def post(self):
        user = self.get_argument("username")
        password = self.get_argument("password")

        users = self.application.db.users
        hit = users.find_one({"user": user})
        if hit:
            if hit["password"] == hashlib.md5(password.encode()).hexdigest():
                self.set_cookie("authenticated_user", user)
                self.set_cookie("authenticated_time",str(time.time()))
                self.redirect("/")
                return

        self.clear_cookie("authenticated_user")
        self.clear_cookie("authenticated_time")
        self.redirect("/login?" + urllib.parse.urlencode({"login_failed": "true"}))


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("authenticated_user")
        self.clear_cookie("authenticated_time")
        self.redirect("/")


class ComposeHandler(BaseHandler):
    compose_result = ""
    def get(self):
        self.render("compose.html")


    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        html = markdown.markdown(content)

        current_time = int(time.time())

        posts = self.application.db.posts
        post = {"title": title, "content" : html, "time" : current_time}
        posts.insert(post)
        self.redirect("/")
