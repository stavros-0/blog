from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional 
#This module includes general purpose database functions and classes such as types and query uilding helpers
import sqlalchemy as sa
# This module provides the support for using modules.
import sqlalchemy.orm as so
from app import login, db, app
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

followers = sa.Table('followers',db.metadata,sa.Column('follower_id',sa.Integer, sa.ForeignKey('user.id'),primary_key=True), 
                     sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),primary_key=True))

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    following: so.WriteOnlyMapped['User'] = so.relationship(secondary=followers, primaryjoin=(followers.c.follower_id==id),
                                                            secondaryjoin=(followers.c.follower_id == id),
                                                            back_populates='followers')
    #primaryjoin indicates the condition that links the entity to the association table
    followers: so.WriteOnlyMapped['User'] = so.relationship(secondary=followers,primaryjoin=(followers.c.followed_id==id),
                                                            secondaryjoin=(followers.c.follower_id == id),
                                                            
                                                            back_populates='following')                                                       
                                                            

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256')
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)


    #performs a query on the following relationship to see if a given user is already included in it
    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None
    
    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)
    
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)
    
    #the join comvines rows from two tables. The combined table is then used during the query
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return(sa.select(Post)
               .join(Post.author.of_type(Author))
               .join(Author.followers.of_type(Follower),isouter=True)
               .where(sa.or_(Follower.id == self.id,
                             Author.id == self.id,
               ))   
               .group_by(Post)          
               .order_by(Post.timestamp.desc())
               )

    def __repr__(self): #how objects will be printed
        return '<User {}>'.format(self.username)
    
#represents blog posts written by users
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))

    #defined with a datetime type and is configured to be indexed, which is useful to retrieve posts in chronological order
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda:datetime.now(timezone.utc))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),index=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
