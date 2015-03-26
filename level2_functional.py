"""
@author: Steve Cassidy
"""

import unittest
from webtest import TestApp
from database import COMP249Db
import main


class Level2FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(main.application)
        # init database
        self.db = COMP249Db()
        self.db.create_tables()
        self.db.sample_data(random=False)
        self.users = self.db.users
        self.posts = self.db.posts

    def testHomepage(self):
        """As a visitor to the site, when I load the
         home page I see a banner with "Welcome to Psst"."""

        response = self.app.get('/')
        self.assertEqual('200 OK', response.status)
        self.assertIn("Welcome to Psst", response)

    def testHomePageListsPosts(self):
        """As a visitor to the site, when I load the home page I see a list of
        up to 50 posts from all users in order of time, most recent first
        """
        
        result = self.app.get('/')
        # should contain text of all posts, need to look for the words because
        # #tags and @mentions will be encoded
        for post in self.posts:
            for word in post[3]:
                self.assertIn(word, result)

        # check the order of posts, look for the date strings
        # and check that they occur in order
        lastloc = -1
        for post in self.posts:
            loc = result.text.find(post[1])
            self.assertNotEqual(-1, loc, "date string '%s' not found in page" % post[1])
            self.assertGreater(loc, lastloc, "date string '%s' occurs out of order" % post[1])
            lastloc = loc


        # not yet checking the 'up to 50' part

    def testUserPage(self):
        """As a visitor to the site, when I load the page for a user I
        see their name and avatar and a list of their posts in order, newest first
        """

        (passwd, nick, avatar) = self.users[0]

        response = self.app.get('/users/%s' % nick)

        # look for the nick
        self.assertIn(nick, response)
        # look for the avatar in an image tag
        self.assertRegex(response.text, "<img src=['\"]?%s['\"]?" % avatar)

        # should contain all posts for this user, check for the date strings
        # also messages for other users should not be there
        # check that dates are in order
        lastloc = -1
        for id, date, msgnick, message in self.posts:
            if msgnick == nick:
                loc = response.text.find(date)
                self.assertIn(date, response.text)
                self.assertGreater(loc, lastloc, "date string '%s' occurs out of order" % date)
            else:
                self.assertNotIn(date, response.text)

    def testUserMentions(self):
        """As a visitor to the site, when I load the mentions
        page for a user, I see a list of all posts that contain the
        @ character followed by the user name
        """

        # choose user Contrary which has two mentions
        (passwd, nick, avatar) = self.users[2]

        response = self.app.get('/mentions/%s' % nick)

        # should contain all posts for this user, check for the date strings
        # also messages for other users should not be there
        for id, date, msgnick, message in self.posts:
            if '@'+nick in message:
                self.assertIn(date, response.text)
            else:
                self.assertNotIn(date, response.text)

if __name__ == "__main__":
    unittest.main()