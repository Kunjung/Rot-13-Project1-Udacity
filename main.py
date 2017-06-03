import jinja2, os
import webapp2

import birthday
import re


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

form="""
<form method="post">
	What is your Birthday?
	<br>
	<label>Month
		<input type="text" name="month" value="%(month)s">
	</label>
	<label>Day
		<input type="text" name="day" value="%(day)s">
	</label>
	<label>Year
		<input type="text" name="year" value="%(year)s">
	</label>
	<div style="color: red">%(error)s</div>
	<br>
	<br>
	<input type="submit">
</form>
"""

class BaseHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render(self, template, **kw):
		self.write(render_str(template, **kw))

# Unit 2 / Rot 13
class Rot13(BaseHandler):
	def get(self):
		self.render('rot13.html')

	def post(self):
		rot13 = ''
		text = self.request.get('text')
		if text:
			rot13 = text.encode('rot13')

		self.render('rot13.html', text=rot13)


# BirthDay Validator
class MainPage(webapp2.RequestHandler):
	def write_form(self, error="", month="", day="", year=""):
		self.response.write(form % {"error": error,
									"month": birthday.escape_html(month),
									"day": birthday.escape_html(day),
									"year": birthday.escape_html(year)})

	def get(self):
		self.write_form()

	def post(self):
		user_month = self.request.get("month")
		user_day = self.request.get("day")
		user_year = self.request.get("year")

		month = birthday.valid_month(user_month)
		day = birthday.valid_day(user_day)
		year = birthday.valid_year(user_year)

		if not (month and day and year):
			self.write_form("That doesn't look valid my friend",
							user_month,
							user_day,
							user_year)
		else:
			self.redirect("/thanks")

class Thanks(webapp2.RequestHandler):
	def get(self):
		self.response.write("Thanks, That's a totally Valid Day!")


# Start of Problem Set 2: User Signup

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
	return not email or EMAIL_RE.match(email)

class Signup(BaseHandler):
	def get(self):
		self.render("signup.html")

	def post(self):
		have_error = False
		
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		params = dict(username = username, email = email)

		if not valid_username(username):
			have_error = True
			params['error_username'] = 'Invalid Username'

		if not valid_password(password):
			have_error = True
			params['error_password'] = 'Invalid password'

		elif verify != password:
			have_error = True
			params['error_verify'] = 'Passwords donot match'

		if not valid_email(email):
			have_error = True
			params['error_email'] = 'Invalid email'


		if have_error:
			self.render('signup.html', **params)

		else:
			self.redirect('/unit2/welcome?username=' + username)


class Welcome(BaseHandler):
	def get(self):
		username = self.request.get("username")
		if valid_username(username):
			self.render("welcome.html", username=username)
		else:
			self.redirect("/unit2/signup")





app = webapp2.WSGIApplication([('/', MainPage),
								('/thanks', Thanks),
								('/unit2/rot13', Rot13),
								('/unit2/welcome', Welcome),
								('/unit2/signup', Signup)],
								 debug=True)
