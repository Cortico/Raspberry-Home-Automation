#!/usr/bin/env python
"""
Creates an HTTP server with basic auth and websocket communication.
"""
import argparse
import base64
import hashlib
import os
import time
import threading
import webbrowser

import tornado.web

# Hashed password for comparison and a cookie for login cache
ROOT = os.path.normpath(os.path.dirname(__file__))
with open(os.path.join(ROOT, "password.txt")) as in_file:
    PASSWORD = in_file.read().strip()
COOKIE_NAME = "camp"

class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        if args.require_login and not self.get_secure_cookie(COOKIE_NAME):
            self.redirect("/login")
        else:
            self.render("index.html", port=args.port, returnssh=">")


class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("login.html")

    def post(self):
        user = self.get_argument("user", "")
        password = self.get_argument("password", "")
        if hashlib.sha512(password).hexdigest() == PASSWORD and user == "diogo":
            self.set_secure_cookie(COOKIE_NAME, str(time.time()))
            self.redirect("/")
        else:
            time.sleep(1)
            self.redirect(u"/login?error")

#class PlayHandler(tornado.web.RequestHandler):
#
#    def get(self):
#        self.render("index.html")
#
#    def post(self):
#        song = self.get_argument("musica", "")
#        os.system('mpg321 song/' + song + ' &')
#        self.redirect("/")

class SSHCommand(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")

    def post(self):
        ssh = self.get_argument("ssh", "")
        p = os.popen(ssh,"r").readlines()
        retorno = "".join(p)
        self.render("index.html", port=args.port, returnssh=retorno)

parser = argparse.ArgumentParser(description="Starts a webserver that "
                                 "connects to a webcam.")
parser.add_argument("--port", type=int, default=8000, help="The "
                    "port on which to serve the website.")
parser.add_argument("--resolution", type=str, default="low", help="The "
                    "video resolution. Can be high, medium, or low.")
parser.add_argument("--require-login", action="store_true", help="Require "
                    "a password to log in to webserver.")
parser.add_argument("--use-usb", action="store_true", help="Use a USB "
                    "webcam instead of the standard Pi camera.")
args = parser.parse_args()

handlers = [(r"/", IndexHandler), (r"/login", LoginHandler), (r"/ssh",SSHCommand),
            (r"/play",PlayHandler),
            (r"/websocket", WebSocket),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': ROOT})]
application = tornado.web.Application(handlers, cookie_secret=PASSWORD)
application.listen(args.port)

tornado.ioloop.IOLoop.instance().start()
