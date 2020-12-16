"""User Views tests."""

import os
from unittest import TestCase
from flask import session
from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test_2"

# Now we can import app

from app import app, CURR_USER_KEY

# app.config['TESTING'] = True
# app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserViewsTestCase(TestCase):
    """test views for user."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        
        user_1 = User.signup("user1",'user1@gmail.com','password', None)
        user_2 = User.signup("user2",'user2@gmail.com','password', None)
        user_3 = User.signup("user3",'user3@gmail.com','password', None)
        user_4 = User.signup("user4",'user4@gmail.com','password', None)
        
        db.session.add_all([user_1,user_2,user_3,user_4])
        db.session.commit()
        self.user_1 = user_1
        self.user_2 = user_2
        self.user_3 = user_3
        self.user_4 = user_4
        msg_1 = Message(text="thisisatest",user_id=self.user_1.id)
        msg_2 = Message(text="second",user_id=self.user_1.id)
        msg_3 = Message(text="three",user_id=self.user_2.id)
        msg_4 = Message(text="four",user_id=self.user_2.id)
        self.msg_1 = msg_1
        self.msg_2 = msg_2
        self.msg_3 = msg_3
        self.msg_4 = msg_4
        
        db.session.add_all([msg_1,msg_2,msg_3,msg_4])
        db.session.commit()


    def tearDown(self):
        '''Clean up test db or any bad transaction '''
        db.session.rollback()

    def test_root(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('<a href="/signup" class="btn btn-primary">Sign up</a>',html)
    
    def test_signup(self):
        with self.client as client:
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>',html)
    
    def test_login_get(self):
        with self.client as client:
            resp = client.get('/login')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('<form method="POST" id="user_form">', html)

    def test_login_post(self):
        with self.client as client:
            d = {"username":"user1","password":"password"}
            resp = client.post('/login',data=d)
            self.assertEqual(resp.status_code,302)

    def test_login_post_fail(self):
        with self.client as client:
            d = {"username":"user1","password":"wrong"}
            resp = client.post('/login',data=d)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('<form method="POST" id="user_form">', html)

    
    def test_users(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)
            self.assertIn('@user1',html)
            self.assertIn('@user2',html)
            self.assertIn('@user3',html)
            self.assertIn('@user4',html)

    def test_user_show(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_1.id}')
            html = resp.get_data(as_text=True)
            self.assertIn('@user1',html)
            self.assertNotIn('@user2',html)
            self.assertEqual(resp.status_code,200)
        
    
    def test_user_search(self):
        with app.test_client() as client:
            resp = client.get(f'/users?q={self.user_1.username}')
            html = resp.get_data(as_text=True)
            self.assertIn('@user1',html)
            self.assertNotIn('@user2',html)
            self.assertEqual(resp.status_code,200)

    def setup_follows(self):
        follow_1 = Follows(user_being_followed_id=self.user_1.id, user_following_id=self.user_3.id)
        follow_2 = Follows(user_being_followed_id=self.user_2.id, user_following_id=self.user_4.id)
        db.session.add_all([follow_1,follow_2])
        db.session.commit()


    def test_user_show_followers(self):
        self.setup_follows()
        with self.client as client:
            
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_1.id
            resp = client.get(f'/users/{self.user_1.id}/followers')
            html = resp.get_data(as_text=True)
            self.assertIn('@user3',html)
            self.assertNotIn('@user2',html)
            self.assertEqual(resp.status_code,200)
                
    def test_user_show_following(self):
        self.setup_follows()
        with self.client as client:
            
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_3.id
            resp = client.get(f'/users/{self.user_3.id}/following')
            html = resp.get_data(as_text=True)
            self.assertIn('@user1',html)
            self.assertNotIn('@user2',html)
            self.assertEqual(resp.status_code,200)
    
    def test_user_show_following_unauth(self):
        self.setup_follows()
        with self.client as client:
            resp = client.get(f'/users/{self.user_3.id}/following',follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('<a href="/signup" class="btn btn-primary">Sign up</a>',html)
            
    def test_user_show_followers_unauth(self):
        self.setup_follows()
        with self.client as client:
            resp = client.get(f'/users/{self.user_3.id}/followers',follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('<a href="/signup" class="btn btn-primary">Sign up</a>',html)
    
    def setup_likes(self):
        like_1 = Likes(user_id=self.user_3.id, message_id=self.msg_1.id)
        like_2 = Likes(user_id=self.user_4.id, message_id=self.msg_2.id)
        db.session.add_all([like_1,like_2])
        db.session.commit()
    
    def test_user_likes_view(self):
        self.setup_likes()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_3.id
            resp = client.get(f'/users/{self.user_3.id}/likes')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('thisisatest',html)

    def test_user_like(self):
        
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_3.id
            resp = client.post(f'/users/add_like/1',follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            like_count = Likes.query.filter(Likes.user_id== self.user_3.id).count()
            self.assertEqual(like_count,1)
            
    def test_user_unlike(self):
        self.setup_likes()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_3.id
            like_count_before = Likes.query.filter(Likes.user_id== self.user_3.id).count()
            self.assertEqual(like_count_before,1)

            resp = client.post(f'/users/add_like/1',follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            like_count_after = Likes.query.filter(Likes.user_id== self.user_3.id).count()
            self.assertEqual(like_count_after,0)

    def test_like_unauth(self):
        with self.client as client:
            resp = client.post(f'/users/add_like/1',follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn('<a href="/signup" class="btn btn-primary">Sign up</a>',html)