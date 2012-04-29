#!/usr/bin/env python

import tornado.web

import setting

import hashlib
import time
import datetime
import urllib.parse


class BaseHandler(tornado.web.Requesthandler):
    def verifyuser(self, user, time):
        hit = self.application.db.users.find_one({"user": user})
        if hit:
            if datetime.datetime.now() - datetime.datetime.fromtimestamp(float(time))  < datetime.timedelta(days = setting.COOKIE_EXPIRE_DAYS):
                return True

        return False


class HomeHandler(BaseHandler):
    def get(self):
        if verifyuser(self.get_cookie("authenticated_user"), self.get_cookie("authenticated_time")):
            self.render("home.html", user_status = self.get_cookie("authenticated_user"))
        else:
            self.render("heme.html", user_status = "Not logged in.")


class LoginHandler(BaseHandler):
    def get(self):
        if self.get_argument("login_failed"):
            self.render("login.html", login_result = "Login failed!")
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

        self.redirect("/login?" + urllib.parse.encode({"login_failed": "true"}))


