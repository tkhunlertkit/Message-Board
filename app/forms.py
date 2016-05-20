from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from .models import User

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.original_nickname == self.nickname.data:
            return True

        if User.query.filter_by(nickname=self.nickname.data).first() is None:
            return True
        else:
            self.nickname.errors.append('This nickname already in use. Please choose a different nickname')
            return False

class PostForm(Form):
    comment = TextAreaField('comments', validators=[Length(min=0, max=140)])
