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
from  bson.objectid import ObjectId


class BaseHandler(tornado.web.RequestHandler):
    def verifyuser(self, user, time):
        hit = self.application.db.users.find_one({"user": user})
        if hit:
            if datetime.datetime.now() - datetime.datetime.fromtimestamp(float(time))  < datetime.timedelta(days = setting.COOKIE_EXPIRE_DAYS):
                return True

        return False


class PageHandler(BaseHandler):
    current_page = 0
    login_success = False
    user_status = "Not logged in."    
    
    def generate_pages(self, page_list):
        left_most = self.current_page - 4  if (self.current_page - 4) >= 1 else 1
        right_most = self.current_page + 4 if (self.current_page + 4) <= page_list[-1] else page_list[-1]
        return list(range(left_most, right_most + 1))

    def get(self, pagenumber): 
        if self.verifyuser(self.get_cookie("authenticated_user"), self.get_cookie("authenticated_time")):
            self.user_status = self.get_cookie("authenticated_user")
            self.login_success = True

        self.current_page = int(pagenumber)
        posts_number = self.application.db.posts.find().count()
        if  posts_number > 0:
            pages, remainder = divmod(posts_number, setting.POSTS_PER_PAGE) 
            if remainder > 0:
                pages += 1
            page_list = self.generate_pages(list(range(1, pages + 1)))
            if self.current_page == 1:
                posts = self.application.db.posts.find().sort("time", pymongo.DESCENDING).limit(setting.POSTS_PER_PAGE)
            else:
                posts = self.application.db.posts.find().sort("time", pymongo.DESCENDING) \
                            .skip((self.current_page - 1)* setting.POSTS_PER_PAGE) \
                                    .limit(setting.POSTS_PER_PAGE)
        else:
            posts = []
            page_list = []
        self.render("home.html", posts = posts, pages= page_list, current_page = self.current_page)



class HomeHandler(PageHandler):
    def get(self):
        return PageHandler.get(self, 1)


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
        post = {"title": title, "content" : content, "html" : html, "time" : current_time}
        posts.insert(post)
        self.redirect("/")


class EditHandler(BaseHandler):
    edit_result = ""
    def get(self, edit_id):
        post = self.application.db.posts.find_one({"_id": ObjectId(edit_id)})
        self.render("edit.html", post = post)

    def post(self, edit_id):
        title = self.get_argument("title")
        content = self.get_argument("content")
        html = markdown.markdown(content)

        try:
            self.application.db.posts.update({"_id": ObjectId(edit_id)},
                    {"$set": {"title": title, "content" : content, "html" : html}} )
            self.redirect("/")
        except e:
            edit_result = "update failed."
            self.redirect("/edit/" + edit_id)
        

class DeleteHandler(BaseHandler):
    def get(self, delete_id):
        posts = self.application.db.posts
        posts.remove({"_id" : ObjectId(delete_id)})
        self.redirect("/")

