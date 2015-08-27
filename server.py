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
import RPi.GPIO as GPIO

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

class SwitchOn(tornado.web.RequestHandler):

   def get(self):
       GPIO.output(12, True);
       print "coffee on"
       self.redirect("/")

class SwitchOff(tornado.web.RequestHandler):

   def get(self):
       GPIO.output(12, False);
       print "coffee off"
       self.redirect("/")

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
parser.add_argument("--require-login", action="store_true", help="Require "
                    "a password to log in to webserver.")
parser.add_argument("--gpio", type=int,  default=12, help="Allows you "
                    "to choose the GPIO port to switch.")
args = parser.parse_args()

handlers = [(r"/", IndexHandler), (r"/turnOn", SwitchOn), (r"/turnOff", SwitchOff),
            (r"/login", LoginHandler), (r"/ssh",SSHCommand),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': ROOT})]
application = tornado.web.Application(handlers, cookie_secret=PASSWORD)
application.listen(args.port)
GPIO.setup(args.gpio, GPIO.OUT)

tornado.ioloop.IOLoop.instance().start()
