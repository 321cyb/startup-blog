#!/usr/bin/env python


import setting


import tornado.web
import tornado.ioloop
import handlers



class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                   ]
                settings = dict(
                       template_path = "template/",
                       static_path   = "static/"
                   )
                tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
        app = Application()
        app.listen(setting.LISTEN_PORT)
        tornado.ioloop.IOLoop.Instance().start()
