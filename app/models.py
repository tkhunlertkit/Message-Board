from app import db
from hashlib import md5

##### User model #####
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def serialize(self, size=50):
        me = {
            'id': self.id,
            'email': self.email,
            'nickname': self.nickname,
            'about_me': self.about_me,
            'last_seen': self.last_seen,
            'img_src': self.avatar(size)
        }
        return me

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while User.query.filter_by(nickname = nickname + str(version)).first() is not None:
            version += 1
        return nickname + str(version)


##### Post Model #####
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
            'nickname': self.author.nickname,
            'user_id': self.user_id
        }

    def __repr__(self):
        return '<Post %r>' % (self.body)


#### Conversation Model #####
# class Conversation(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(30), nullable=False)
#     posts = db.relationship('Post', backref='conversation', lazy='dynamic')
