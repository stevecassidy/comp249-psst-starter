"""
@author: Steve Cassidy
"""
import unittest
from webtest import TestApp
from database import COMP249Db
import main, users


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
        # but we see the user name
        self.assertIn(nick, response2)
        # and a logout form
        self.assertIn('logoutform', response2.forms)
        logoutform = response2.forms['logoutform']
        self.assertEqual('/logout', logoutform.action)


        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(warnings='ignore')