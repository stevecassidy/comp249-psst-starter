'''
@author: Steve Cassidy

'''
import unittest

import interface
from database import COMP249Db


class LevelAUnitTests(unittest.TestCase):
    
    
    def setUp(self):
        # open an in-memory database for testing
        self.db = COMP249Db(':memory:')
        self.db.create_tables()
        self.db.sample_data(random=False)


        self.posts = self.db.posts

    def test_post_list(self):
        """Test that post_list returns all posts"""

        # first get all posts
        posts = interface.post_list(self.db)

        self.assertEqual(len(self.posts), len(posts))

        # now restrict to one user
        posts = interface.post_list(self.db, usernick='Mandible')
        self.assertEqual(3, len(posts))

        # try a user with no posts
        posts = interface.post_list(self.db, usernick='jb@up.com')
        self.assertEqual(0, len(posts))

        # try a user who doesn't exist
        posts = interface.post_list(self.db, usernick='not@real.com')
        self.assertEqual(0, len(posts))

        # now look at the limit argument
        posts = interface.post_list(self.db, limit=3)
        self.assertEqual(3, len(posts))

        posts = interface.post_list(self.db, limit=1)
        self.assertEqual(1, len(posts))

        # limit higher than number of posts
        posts = interface.post_list(self.db, limit=100)
        self.assertEqual(10, len(posts))




    def test_post_list_mentions(self):
        """Test getting a list of posts mentioning a user"""

        user1 = 'Contrary'
        user2 = 'Bobalooba'
        user3 = 'Mandible'

        posts = interface.post_list_mentions(self.db, usernick=user1)
        # should include only posts with @Contrary
        self.assertEqual(2, len(posts))
        self.assertListEqual([2, 5], [p[0] for p in posts])



    def test_post_html(self):
        """Test conversion of posts to HTML"""

        # plain text doesn't change
        text = "Hello World!"
        self.assertEqual(text, interface.post_to_html(text))

        # quoting HTML
        text = "<p>Hello World</p>"
        html = interface.post_to_html(text)
        self.assertEqual("&lt;p&gt;Hello World&lt;/p&gt;", html)

        # quoting HTML with attributes
        text = "<p class='foo'>Hello World</p>"
        html = interface.post_to_html(text)
        self.assertEqual("&lt;p class='foo'&gt;Hello World&lt;/p&gt;", html)

        # quoting HTML entities
        text = "Fish & Chips"
        html = interface.post_to_html(text)
        self.assertEqual("Fish &amp; Chips", html)

        # links
        text = "<p>Hello World http://example.org/ is it</p>"
        html = interface.post_to_html(text)
        self.assertEqual("&lt;p&gt;Hello World <a href='http://example.org/'>http://example.org/</a> is it&lt;/p&gt;", html)

        # links with stuff
        text = "<p>Hello World http://example.org/home_page.html is it</p>"
        html = interface.post_to_html(text)
        self.assertEqual("&lt;p&gt;Hello World <a href='http://example.org/home_page.html'>http://example.org/home_page.html</a> is it&lt;/p&gt;", html)


    def test_post_html_mentions(self):
        """Test conversion of @mentions in posts to HTML"""

        # mentions
        text = "<p>Hello World @Bobolooba</p>"
        html = interface.post_to_html(text)
        self.assertEqual("&lt;p&gt;Hello World <a href='/users/Bobolooba'>@Bobolooba</a>&lt;/p&gt;", html)

        # word internal period is allowed
        text = "<p>Hello World @steve.cassidy</p>"
        html = interface.post_to_html(text)
        self.assertEqual("&lt;p&gt;Hello World <a href='/users/steve.cassidy'>@steve.cassidy</a>&lt;/p&gt;", html)

        # word final period is not part of the name
        text = "Hello World @Cat."
        html = interface.post_to_html(text)
        self.assertEqual("Hello World <a href='/users/Cat'>@Cat</a>.", html)

        # word final period followed by space is not part of the name
        text = "Hello World @Cat. Hi!"
        html = interface.post_to_html(text)
        self.assertEqual("Hello World <a href='/users/Cat'>@Cat</a>. Hi!", html)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()