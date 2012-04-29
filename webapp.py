#!/usr/bin/env python


import setting


import tornado.web
import tornado.ioloop
import handlers
import pymongo



class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                        ("/", handlers.HomeHandler),
                        ("/login", handlers.LoginHandler)
                   ]
                settings = dict(
                       template_path = "template/",
                       static_path   = "static/",
                       debug         = True
                   )
                tornado.web.Application.__init__(self, handlers, **settings)

                #initiate mongodb
                conn = pymongo.Connection(setting.MONGODB_HOST, setting.MONGODB_PORT)
                self.db = conn.blog 



if __name__ == "__main__":
        app = Application()
        app.listen(setting.LISTEN_PORT)
        tornado.ioloop.IOLoop.Instance().start()
