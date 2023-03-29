If you want to run this on localhost you will need to make sure you have the python
modules installed that are in requirements.txt

If this was to be deployed you would have to set secret key in **init**.py file

If you are not using the sqlite db that is in instance/site.db then you will need to run
the following:

create virtual env by running
$ source venv/bin/activate
you should see <venv> in command prompt

enter python shell
python

then create db by typing

 from mktime import app, db
 app.app_context().push()
 db.create_all()

each of the above commands should return without error, however you will be missing products and users.

To log in 1st register a user.
Then login.
You will notice that you have access to a different navbar
and the following dummy admin routes will be available too
admin/product/new to add new products
admin/posts to read the posts from the contact form

All other routes are available from clicking through the website.

You should be able to register a user, login, contact the site, logout, view 6 products,
and see a landing page, an about page.
