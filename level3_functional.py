"""
@author: Steve Cassidy
"""
import unittest
from webtest import TestApp
from database import COMP249Db
import main, users

from random import choice


class Level3FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(main.application)
        # init database
        self.db = COMP249Db()
        self.db.create_tables()
        self.db.sample_data(random=False)
        self.users = self.db.users
        self.posts = self.db.posts
            
    def doLogin(self, user, password):
        """Perform a login with some validation along the way"""
        
        response = self.app.get('/')

        loginform = response.forms['loginform']

        self.assertIsNotNone(loginform, "no form with id loginform in the page")

        # login form action should be /login
        self.assertEqual('/login', loginform.action, "login form action should be '/login'")
 
        # the form has a user field
        self.assertIn('nick', loginform.fields)
        
        # and a password field
        self.assertIn('password', loginform.fields)

        loginform['nick'] = user
        loginform['password'] = password

        response = loginform.submit()

        return response

    def testLoginForms(self):
        """As a visitor to the site, when I load the home page, 
        I see a form with entry boxes for email and password and a button labelled Login."""

        (password, nick, avatar) = self.users[0]
                
        # As a registered user, when I enter my email address (bob@here.com) and password 
        # (bob) into the login form and click on the Login button,
        
        response = self.doLogin(nick, password)
        
        self.assertEqual('303 See Other', response.status)
        self.assertEqual('/', response.headers['Location'])
        
        # The response also includes a cookie with the name 
        # sessionid that contains some kind of random string.

        self.assertIn(users.COOKIE_NAME, self.app.cookies)
        sessionid = self.app.cookies[users.COOKIE_NAME]

    def testLoginError(self):
        """As a registered user, when I enter my email address but get my 
        password wrong and click on the Login button, the page I get in 
        response contains a message "Login Failed, please try again". 
        The page also includes another login form."""

         
        (password, nick, avatar) = self.users[0]

        # try an invalid password

        response = self.doLogin(nick, 'not the password')

        # should see a page returned with the word Error somewhere
        self.assertEqual('200 OK', response.status)
        self.assertIn("Failed", response)

        # Should not have a cookie
        self.assertNotIn(users.COOKIE_NAME, self.app.cookies)
    
    def testLoginPagesLogoutForm(self):
        """As a registered user, once I have logged in,
         every page that I request contains my name and the logout form."""

        (password, nick, avatar) = self.users[0]

        response1 = self.doLogin(nick, password)
        response2 = self.app.get('/')

        # no login form
        self.assertNotIn('loginform', response2.forms)

        # but a logout form
        self.assertIn('logoutform', response2.forms)
        logoutform = response2.forms['logoutform']
        self.assertEqual('/logout', logoutform.action)

        # and the message "Logged in as XXX"
        self.assertIn("Logged in as %s" % nick, response2)

    def testLogoutForm(self):
        """As a registered user, once I have logged in, if I click on the Logout
        button in a page, the page that I get in response is the site home
        page which now doesn't have my name and again shows the login form."""

        (password, nick, avatar) = self.users[0]

        response1 = self.doLogin(nick, password)
        response2 = self.app.get('/')

        # and a logout form
        self.assertIn('logoutform', response2.forms)
        logoutform = response2.forms['logoutform']

        response3 = logoutform.submit()
        # response should be a redirect
        self.assertEqual('303 See Other', response3.status)
        self.assertEqual('/', response3.headers['Location'])

        response4 = self.app.get('/')
        # should see login form again
        loginform = response4.forms['loginform']
        self.assertIsNotNone(loginform, "no form with id loginform in the page")



    def testCreatePost(self):
        """As a registered user, I can fill out a form on the main
        page to create a new post, when I submit the form I am redirected
        to the main page and my new post appears in the list"""

        (password, nick, avatar) = self.users[0]

        # generate a random string to look for in the post, use it in a URL that should be
        # turned into a link
        letters = "abcdefghijklmnopqrstuvwxyz1234560928"
        randomstring = ''.join([choice(letters) for i in range(20)])
        url = "http://example.org/url/" + randomstring

        testmessage = "This is a new message that mentions @Mandible and has a "+ url + " in it."

        response = self.doLogin(nick, password)
        response = self.app.get('/')

        self.assertIn('postform', response)

        form = response.forms['postform']
        self.assertEqual('/post', form.action, "post form action should be '/post'")

        form['post'] = testmessage

        response = form.submit()

        # check response

        self.assertEqual('303 See Other', response.status)
        self.assertEqual('/', response.headers['Location'])

        # fetch home page and look for our message

        response = self.app.get('/')
        self.assertIn(randomstring, response)

        # also look for the mention as a link
        html = response.html
        links = html.find_all('a', attrs={'href': '/users/Mandible'})
        self.assertGreaterEqual(len(links), 1, "can't find link to user page for Mandible after posting")

        # and the URL as a link
        links = html.find_all('a', attrs={'href': url})
        self.assertGreaterEqual(len(links), 1, "can't find link to url " + url + " after posting")





if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(warnings='ignore')