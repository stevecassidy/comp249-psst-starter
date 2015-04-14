'''
Created on Mar 26, 2012

@author: steve
'''

import sqlite3
import time
from random import randint, choice


class COMP249Db():
    '''
    Provide an interface to the database for a COMP249 web application
    '''


    def __init__(self, dbname="comp249.db"):
        '''
        Constructor
        '''
        
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname)
        ### ensure that results returned from queries are strings rather
        # than unicode which doesn't work well with WSGI
        self.conn.text_factory = str
        
    def cursor(self):
        """Return a cursor on the database"""
        
        return self.conn.cursor()
    
    def commit(self):
        """Commit pending changes"""
        
        self.conn.commit()
        
    def delete(self):
        """Destroy the database file"""
        pass
        
        
    def crypt(self, password):
        """Return a one-way hashed version of the password suitable for
        storage in the database"""
        
        import hashlib
        
        return hashlib.sha1(password.encode()).hexdigest()
        

    def create_tables(self):
        """Create and initialise the database tables
        This will have the effect of overwriting any existing
        data."""
        
        
        sql = """
DROP TABLE IF EXISTS users;
CREATE TABLE users (
           nick text unique primary key,
           password text,
           avatar text
);

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
            sessionid text unique primary key,
            usernick text,
            FOREIGN KEY(usernick) REFERENCES users(nick)
);

DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
            id integer unique primary key autoincrement,
            timestamp text default CURRENT_TIMESTAMP,
            usernick text,
            content text,
            FOREIGN KEY(usernick) REFERENCES users(nick)
);

DROP TABLE IF EXISTS votes;
CREATE TABLE votes (
            post text,
            usernick text,
            FOREIGN KEY(post) REFERENCES posts(id),
            FOREIGN KEY(usernick) REFERENCES users(nick)
);

DROP TABLE IF EXISTS follows;
CREATE TABLE follows (
            follower text,
            followed text,
            FOREIGN KEY(follower) REFERENCES users(nick),
            FOREIGN KEY(followed) REFERENCES users(nick)
);


"""

        self.conn.executescript(sql)
        self.conn.commit()
        
    
    def sample_data(self, random=True):
        """Generate some sample data for testing the web
        application. Erases any existing data in the
        database
        If random is True, generate  100 random posts,  otherwise
        generate fixed set of data to use for testing."""
        
                #  pass,   nick             avatar
        self.users = [('bob', 'Bobalooba', 'http://robohash.org/bob'),
                 ('jim', 'Jimbulator', 'http://robohash.org/jim'),
                 ('mary', 'Contrary', 'http://robohash.org/mary'),
                 ('jb', 'Bean', 'http://robohash.org/jb'),
                 ('mandible', 'Mandible', 'http://robohash.org/mandible'),
                 ('bar', 'Barfoo', 'http://robohash.org/bar'),
        ]
        #  Robots lovingly delivered by Robohash.org


        cursor = self.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM posts")

        # create one entry for each user
        for password, nick, avatar in self.users:
            sql = "INSERT INTO users (nick, password, avatar) VALUES (?, ?, ?)"
            cursor.execute(sql, (nick, self.crypt(password), avatar))
            sql = "INSERT INTO follows (followed, follower) VALUES (?, ?)"
            cursor.execute(sql, [nick, nick])


        if random:

            # generate some random posts

            # t is a number of seconds in the past, we subtract it from the current time
            # to get a time in the past for a post
            t = 0
            for i in range(100):
                user = choice(self.users)
                mentions = ['@'+u[1] for u in self.users if u != user]

                content = gentext(user[1], mentions)

                # generate a timestamp, not normally needed because the timestamp field
                # defaults to the current time, but we want to generate posts at different
                # times for testing so we'll set the timestamp for each one
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()-t))

                sql = "INSERT INTO posts (usernick, timestamp, content) VALUES (?, ?, ?)"

                cursor.execute(sql, (user[1], timestamp, content))

                # increment the time we subtract
                t += 3013

            # commit all updates to the database
            self.commit()

        else:
            self.fixed_data()

    def fixed_data(self):
        """Generate a fixed data set for testing purposes"""

        self.posts = [
            (1, '2015-02-20 01:45:06', 'Mandible',    'wkwaai yiynhmg rdcxnwuhy yxxzlieaxe yu waez efh odiipzqep cp qsaqp gkhhyxkb raguklag #ox qbml nuhb #mtzw yctpzdx uxxqibyw zhysw ugidbqii'),
            (2, '2015-02-20 00:54:53', 'Barfoo',      'edukmb zankyyu panhipscgo zkvoyg gaaeuogdzn lhpiemoaui ave aruckns conk we @Contrary nlyixitpd fianqsj #ync iou yoeifeodjo  sxxms umpcvu'),
            (3, '2015-02-20 00:04:40', 'Jimbulator',  '#sre ydpwg kau elepeeu dukouvya #ax jji #cvrwu yccq mxbdehwyna hyhhj oqyiibzrfl nilytlwqws yppu plggqfsfyn ggf snzxlxo qdjzzg iyjc '),
            (4, '2015-02-19 23:14:27', 'Contrary',    '#cfsidisk xvucuio ww yqoowit cjshcohaad euau vbzylol acpxixpsh qay @Bobalooba okl #gjyep'),
            (5, '2015-02-19 22:24:14', 'Mandible',    'mhdckmcys tdwioaxxa bviwczux wuhbalaa yiul xm cvauk stouea eexmahg vi uwy iy qp cifog eizjzmsaae eiixs aam #gye @Contrary zt '),
            (6, '2015-02-19 21:34:01', 'Mandible',    'eywam ooh ftmjr #swgsdd sp @Jimbulator frfikgij nquuz ovuezj edlxcejw'),
            (7, '2015-02-19 20:43:48', 'Bobalooba',   'uoro hgjkpzdyyx jsjtl tbnia egoetouzda vayiftdnlh tnh cpzd #rucaecv olkao osit bdqi vry oiweusczq wepf lptp gud pooezehvqu  oaywaeu '),
            (8, '2015-02-19 19:53:35', 'Contrary',    'qhopqrquy ayiwktwn uluefr oei savjdu #nrurcdrbq vuzdoaco trzbuj zpjetma xdjeooprhe fsvt rnx #gquax ctizac ssun nfdtiz #zocpybi @Bean'),
            (9, '2015-02-19 19:03:22', 'Barfoo',      'nx tdeekuyt inyevkn mravuos dwkbtp aaolctomnj ecleerbm raynuui exiymoz lyeywzt cnzyykgfkg jn ievbfe zfpaxga  guapoe @Jimbulator '),
            (10, '2015-02-19 18:13:09', 'Jimbulator', 'ieqm yaa ar cwynuy efil ewelkagj ujasyn nwyenbd ziirqnwek oycu eghrbew ybjyp ew na focbq jxfqarocy jsaa  tt atoitu ojnpswqk')]

        cursor = self.cursor()

        for post in self.posts:

            sql = "INSERT INTO posts (id, timestamp, usernick, content) VALUES (?, ?, ?, ?)"

            cursor.execute(sql, post)

        # commit all updates to the database
        self.commit()

def gentext(author, mentions):
    """Generate some random text for development purposes"""

    # vowels appear twice to make them twice as likely as consonants
    letters = "aeiouybcdfghjklmnpqrstvwxzaeiouy"

    words = [author]
    length = 0
    # make text of up to 20 words
    for i in range(randint(5,50)):
        word = []
        # make a word by choosing some letters
        # sometimes make it a hash tag
        if randint(0,100) > 90:
            word.append('#')
        for j in range(randint(2, 10)):
            word.append(choice(letters))
        words.append(''.join(word))
        length += len(words[-1])
        if length >=140:
            break

    # add a mention
    words.insert(randint(0, len(words)), choice(mentions))
    return ' '.join(words)


if __name__=='__main__':
    # if we call this script directly, create the database and make sample data
    db = COMP249Db()
    db.create_tables()
    db.sample_data()