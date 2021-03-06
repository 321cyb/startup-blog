#!/usr/bin/env python

import hashlib
import time
import datetime
import logging
import functools
import urllib.parse

import tornado.web
import pymongo
from  bson.objectid import ObjectId


import setting
import front
import utils
from thirdAuth.weibo import WeiboMixin

def just_get_user_info(func):
        @functools.wraps(func)
        def handle(self, *args, **kwargs):
            user = self.get_current_user()
            if user:
                self.logged_in = True
                self.user = user

            func(self, *args, **kwargs)

        return handle


#In db, every post entry has these fields:
#title, author, time, markdown, html

#In db, every user has these fields:
#name, provider, uid, password, salt, access_token

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
        return front.Post(post_id, post["title"], post["author"], post["mtime"], post["ctime"], post["markdown"], post["html"])

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
                posts = self.application.db.posts.find().sort("ctime", pymongo.DESCENDING).limit(setting.POSTS_PER_PAGE)
            else:
                posts = self.application.db.posts.find().sort("ctime", pymongo.DESCENDING) \
                        .skip((pagenumber - 1) * setting.POSTS_PER_PAGE) \
                        .limit(setting.POSTS_PER_PAGE)

            this_page_posts = []
            for post in posts:
                this_page_posts.append(front.Post(post["_id"], post["title"], post["author"], post["mtime"], post["ctime"],  post["markdown"], post["html"]))

            return (this_page_posts, page_list)
        else:
            return ([], [])

    def get_current_user(self):
        user = self.get_secure_cookie("authenticated_user")
        if user:
            hit = self.application.db.users.find_one(utils.provider_and_uid(user.decode()))
            if hit:
                return front.User(hit["name"], hit["provider"], hit["uid"])

        return None

    def get_login_url(self):
        return "/"


class PageHandler(BaseHandler):
    @just_get_user_info
    def get(self, pagenumber): 
        current_page = int(pagenumber)
        (posts, page_list) = self.get_posts_of_page(current_page)
        self.render("home.html", posts = posts, pages= page_list, current_page = current_page)



class HomeHandler(PageHandler):
    def get(self):
        login_failed = self.get_arguments("login_failed")
        if len(login_failed) > 0:
            self.result_message = "Login failed!"
 
        return PageHandler.get(self, 1)


class EntryHandler(BaseHandler):
    @just_get_user_info
    def get(self, entry_id):
        post = self.get_one_post(entry_id)
        if post:
            self.render("entry.html", post = post)
        else:
            self.send_error(404)

class LoginHandler(BaseHandler):
    def post(self):
        user = self.get_argument("username")
        password = self.get_argument("password")

        users = self.application.db.users
        hit = users.find_one({"name": user, "provider": ""})
        if hit and hit["password"] == hashlib.sha256(password.encode() + hit["salt"]).hexdigest():
                self.set_secure_cookie("authenticated_user", user, expires_days = setting.COOKIE_EXPIRE_DAYS)
                self.redirect("/")
                return

        self.clear_cookie("authenticated_user")
        self.redirect("/?" + urllib.parse.urlencode({"login_failed": "true"}))

class WeiboLoginHandler(BaseHandler, WeiboMixin):
    def create_user_if_necessary(self, user):
         if not self.application.db.users.find_one({"provider": "weibo", "uid": str(user["id"])}):
             self.application.db.users.insert({"name":user["screen_name"], "provider": "weibo", "uid": str(user["id"]), "password": "", "salt": "", 
                  "access_token": user["access_token"]})

    @tornado.web.asynchronous
    def get(self):
          if self.get_argument("code", False):
              self.get_authenticated_user( redirect_uri=setting.WEIBO_REDIRECT_URL,
                            client_id=setting.WEIBO_APPKEY,
                            client_secret=setting.WEIBO_APP_SECRET,
                            code=self.get_argument("code"),
                            callback=self.async_callback(self._on_login))
          else:
              self.authorize_redirect(redirect_uri=setting.WEIBO_REDIRECT_URL,
                                              client_id=setting.WEIBO_APPKEY,
                                              extra_params={"response_type": "code"})
    def _on_login(self, user):
         if user:
             self.create_user_if_necessary(user)
             self.set_secure_cookie("authenticated_user", "weibo\x00" + str(user["id"]), expires_days = setting.COOKIE_EXPIRE_DAYS)
         self.redirect("/")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("authenticated_user")
        self.redirect("/")


class ComposeHandler(BaseHandler):

    @just_get_user_info
    @tornado.web.authenticated
    def get(self):
        self.render("compose.html")


    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        html = self.get_argument("html", "")
        logging.error(html)
        author = self.get_current_user().name

        current_time = int(time.time())

        posts = self.application.db.posts
        post = {"title": title, "markdown" : content, "html" : html, "mtime" : current_time, "ctime": current_time, "author": author}
        posts.insert(post)
        self.redirect("/")


class EditHandler(BaseHandler):

    @just_get_user_info
    @tornado.web.authenticated
    def get(self, edit_id):
        post = self.get_one_post(edit_id)
        self.render("edit.html", post = post)

    def post(self, edit_id):
        title = self.get_argument("title", "")
        content = self.get_argument("content", "")
        html =  self.get_argument("html", "")
        current_time = int(time.time())

        try:
            self.application.db.posts.update({"_id": ObjectId(edit_id)},
                    {"$set": {"title": title, "markdown" : content, "html" : html, "mtime": current_time}} )
            self.redirect("/")
        except e:
            edit_result = "update failed." #Wow, this will never show up. fix later.
            self.redirect("/edit/" + edit_id)
        
class FeedHandler(BaseHandler):
    def get(self):
        (posts, page_list) = self.get_posts_of_page(1)
        self.render("feed.xml", posts = posts)

        

class DeleteHandler(BaseHandler):

    @just_get_user_info
    @tornado.web.authenticated
    def get(self, delete_id):
        self.delete_one_post(delete_id)
        self.redirect("/")
        

class JSONTestHandler(BaseHandler):
    def get(self):
        import json
        s = json.dumps({"name": "clybe", "password": "youknow"})
        self.write(s)

