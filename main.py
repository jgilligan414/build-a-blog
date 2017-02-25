#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, cgi, jinja2, os, re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Blog(db.Model):
    title = db.StringProperty(required=True)
    entry = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainBlog(Handler):
    def render_front(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        recent = entries.fetch(limit=5)

        self.render("mainblog.html", title=title, entry=entry, error=error, recent=recent)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_post(self, title="", entry="", error=""):
        self.render("newpost.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_post()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            b = Blog(title=title, entry=entry)
            b.put()

            self.redirect('/blog/%s' % str(b.key().id()))

        else:
            error = "we need both a title and an entry"
            self.render_post(title, entry, error)

class ViewPostHandler(Handler):
    def get(self, id):
        key = Blog.get_by_id(int(id))

        self.render('post.html', key=key)


app = webapp2.WSGIApplication([
    ('/blog', MainBlog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
