#!/usr/bin/env python

import tornado.web

import setting
import front

import hashlib
import time
import datetime
import logging
import urllib.parse

import markdown
import pymongo
from  bson.objectid import ObjectId


class BaseHandler(tornado.web.RequestHandler):
    user = front.User("")
    result_message = ""
    logged_in = False
    def get_one_post(self, post_id):
        '''
        post_id ->  str type
        return  ->  Post type
        '''
        post = self.application.db.posts.find_one({"_id": ObjectId(post_id)})
        return front.Post(post_id, post["title"], post["author"], post["time"], post["markdown"], post["html"])
    def delete_one_post(self, post_id):
        posts = self.application.db.posts
        posts.remove({"_id" : ObjectId(post_id)})
  
    def generate_pages(self, page_list, current_page):
        left_most = current_page - 4  if (current_page - 4) >= 1 else 1
        right_most = current_page + 4 if (current_page + 4) <= page_list[-1] else page_list[-1]
        return list(range(left_most, right_most + 1))

    def get_posts_of_page(self, pagenumber):
        '''
        pagenumber -> int type
        return     -> ([Post], [int]), Posts  and page list
        '''
        posts_number = self.application.db.posts.find().count() # this number may be to be cached.
        if  posts_number > 0:
            pages, remainder = divmod(posts_number, setting.POSTS_PER_PAGE) 
            if remainder > 0:
                pages += 1
            page_list = self.generate_pages(list(range(1, pages + 1)), pagenumber)
            if pagenumber== 1:
                posts = self.application.db.posts.find().sort("time", pymongo.DESCENDING).limit(setting.POSTS_PER_PAGE)
            else:
                posts = self.application.db.posts.find().sort("time", pymongo.DESCENDING) \
                        .skip((self.pagenumber - 1) * setting.POSTS_PER_PAGE) \
                        .limit(setting.POSTS_PER_PAGE)

            this_page_posts = []
            for post in posts:
                this_page_posts.append(front.Blog(post["_id"], post["title"], post["author"], post["time"], post["markdown"], post["html"]))

            return (this_page_posts, page_list)
        else:
            return ([], [])


    def get_user(self):
        user = self.get_secure_cookie("authenticated_user")
        if user:
            if self.application.db.users.find_one({"user": user.decode()}):
                return user.decode()

        return None


class PageHandler(BaseHandler):
    login_success = False
   
    def get(self, pagenumber): 
        if self.get_user():
            self.user_status = self.get_secure_cookie("authenticated_user").decode()
            self.login_success = True

        current_page = int(pagenumber)
        (posts, page_list) = self.get_posts_of_page(current_page)
        self.render("home.html", posts = posts, pages= page_list, current_page = current_page)



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
            if hit["password"] == hashlib.sha256(password.encode() + hit["salt"]).hexdigest():
                self.set_secure_cookie("authenticated_user", user, expires_days = setting.COOKIE_EXPIRE_DAYS)
                self.redirect("/")
                return

        self.clear_cookie("authenticated_user")
        self.redirect("/login?" + urllib.parse.urlencode({"login_failed": "true"}))


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("authenticated_user")
        self.redirect("/")


class ComposeHandler(BaseHandler):
    compose_result = ""
    def get(self):
        if not self.get_user():
            self.redirect("/")
            return
 
        self.render("compose.html")


    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        html = markdown.markdown(content)
        author = self.get_user()

        current_time = int(time.time())

        posts = self.application.db.posts
        post = {"title": title, "markdown" : content, "html" : html, "time" : current_time, "author": author}
        posts.insert(post)
        self.redirect("/")


class EditHandler(BaseHandler):
    edit_result = ""
    def get(self, edit_id):
        if not self.get_user():
            self.redirect("/")
            return
 
        post = self.get_one_post(edit_id)
        self.render("edit.html", post = post)

    def post(self, edit_id):
        title = self.get_argument("title", "")
        content = self.get_argument("content", "")
        html = markdown.markdown(content)

        try:
            self.application.db.posts.update({"_id": ObjectId(edit_id)},
                    {"$set": {"title": title, "markdown" : content, "html" : html}} )
            self.redirect("/")
        except e:
            self.edit_result = "update failed." #Wow, this will never show up. fix later.
            self.redirect("/edit/" + edit_id)
        

class DeleteHandler(BaseHandler):
    def get(self, delete_id):
        if not self.get_user():
            self.redirect("/")
            return

        self.delete_one_post(delete_id)
        self.redirect("/")


