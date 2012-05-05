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
from thirdAuth.weibo import WeiboMixin


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
                        .skip((pagenumber - 1) * setting.POSTS_PER_PAGE) \
                        .limit(setting.POSTS_PER_PAGE)

            this_page_posts = []
            for post in posts:
                this_page_posts.append(front.Post(post["_id"], post["title"], post["author"], post["time"], post["markdown"], post["html"]))

            return (this_page_posts, page_list)
        else:
            return ([], [])

    def cookie_get_user(self):
        '''
        str
        '''
        user = self.get_secure_cookie("authenticated_user")
        if user and self.application.db.users.find_one({"user": user.decode()}):
                return front.User(user.decode())

        return None

    def db_get_user(self, user_name):
        '''
        str -> front.User
        '''
        #What if no such user exist? FIXME!
        user = self.application.db.users.find_one({"user": user_name})
        return front.User(user.user)

    def redirect_if_not_logged_in(func):
        @functools.wraps(func)
        def handle(self, *args, **kwargs):
            user = self.cookie_get_user()
            if user:
                self.logged_in = True
                self.user = user
            elif self.request.path != "/":
                self.redirect("/")
                return

            func(self, *args, **kwargs)

        return handle


class PageHandler(BaseHandler):
    @BaseHandler.redirect_if_not_logged_in
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


class LoginHandler(BaseHandler):
    def post(self):
        user = self.get_argument("username")
        password = self.get_argument("password")

        users = self.application.db.users
        hit = users.find_one({"user": user})
        if hit and hit["password"] == hashlib.sha256(password.encode() + hit["salt"]).hexdigest():
                self.set_secure_cookie("authenticated_user", user, expires_days = setting.COOKIE_EXPIRE_DAYS)
                self.redirect("/")
                return

        self.clear_cookie("authenticated_user")
        self.redirect("/?" + urllib.parse.urlencode({"login_failed": "true"}))

class WeiboLoginHandler(BaseHandler, WeiboMixin):
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
         logging.error(user)
         self.finish()


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("authenticated_user")
        self.redirect("/")


class ComposeHandler(BaseHandler):

    @BaseHandler.redirect_if_not_logged_in
    def get(self):
        self.render("compose.html")


    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        html = self.get_argument("html", "")
        logging.error(html)
        author = self.cookie_get_user().name

        current_time = int(time.time())

        posts = self.application.db.posts
        post = {"title": title, "markdown" : content, "html" : html, "time" : current_time, "author": author}
        posts.insert(post)
        self.redirect("/")


class EditHandler(BaseHandler):

    @BaseHandler.redirect_if_not_logged_in
    def get(self, edit_id):
        post = self.get_one_post(edit_id)
        self.render("edit.html", post = post)

    def post(self, edit_id):
        title = self.get_argument("title", "")
        content = self.get_argument("content", "")
        html =  self.get_argument("html", "")

        try:
            self.application.db.posts.update({"_id": ObjectId(edit_id)},
                    {"$set": {"title": title, "markdown" : content, "html" : html}} )
            self.redirect("/")
        except e:
            edit_result = "update failed." #Wow, this will never show up. fix later.
            self.redirect("/edit/" + edit_id)
        

class DeleteHandler(BaseHandler):

    @BaseHandler.redirect_if_not_logged_in
    def get(self, delete_id):
        self.delete_one_post(delete_id)
        self.redirect("/")


