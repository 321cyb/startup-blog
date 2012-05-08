#!/usr/bin/env python


import setting


import os.path
import logging
import tornado.web
import tornado.ioloop
import handlers
import pymongo



class Application(tornado.web.Application):
        def __init__(self):
                _handlers = [
                        (r"/", handlers.HomeHandler),
                        (r"/login", handlers.LoginHandler),
                        (r"/logout", handlers.LogoutHandler),
                        (r"/compose", handlers.ComposeHandler),
                        (r"/delete/(\w+)", handlers.DeleteHandler),
                        (r"/edit/(\w+)", handlers.EditHandler),
                        (r"/page/(\d+)", handlers.PageHandler),
                        (r"/entry/(\w+)", handlers.EntryHandler),
                        (r"/feed", handlers.FeedHandler),
                        (r"/oauth/weibo",handlers.WeiboLoginHandler),
                        (r"/dependencies/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "dependencies")}),
                        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")})
                   ]
                settings = dict(
                       template_path = os.path.join(os.path.dirname(__file__), "template/"),
                       static_path   = os.path.join(os.path.dirname(__file__), "static/"),
                       cookie_secret = setting.COOKIE_SECRET,
                       debug         = True
                   )
                tornado.web.Application.__init__(self, _handlers, **settings)

                #initiate mongodb
                conn = pymongo.Connection(setting.MONGODB_HOST, setting.MONGODB_PORT)
                self.db = conn.blog 



if __name__ == "__main__":
        app = Application()
        app.listen(setting.LISTEN_PORT)
        tornado.ioloop.IOLoop.instance().start()
