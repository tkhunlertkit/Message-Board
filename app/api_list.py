from app import app, api, db
from flask import Flask, jsonify, abort, g
from .models import Post, User
from flask.ext.restful import Resource, reqparse
from datetime import datetime
from flask.ext.login import login_user, logout_user, current_user, login_required
from datetime import datetime

##### API for posts
class PostAPI(Resource):
    decorators = [login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('body', type=str, required=True,
            help = 'No message body provided', location = 'json')
        super(PostAPI, self).__init__()

    def get(self, nickname = None, message_id = 0):
        print 'message_id is:', message_id
        if nickname is None:
            user_posts = Post.query.filter(Post.id > message_id).order_by('timestamp').all()
        else:
            user = User.query.filter_by(nickname=nickname).first()
            if user is None:
                abort(404)

            user_posts = user.posts.order_by('timestamp desc')

        posts = [post.serialize for post in user_posts]
        return jsonify(posts = posts)

    def post(self, nickname=None):
        """
        Create a new Post
        """
        args = self.reqparse.parse_args()
        if args['body'] == '':
            print 'returning none'
            return None
        post = Post(body=args['body'], user_id=g.user.id, timestamp=datetime.utcnow())
        db.session.add(post)
        db.session.commit()
        p = post.serialize
        res = jsonify(posts = [p])
        return res

    def put(self, nickname=None):
        pass

class UserAPI(Resource):
    decorators = [login_required]

    def get(self, user_id=None):
        if user_id is not None:
            users = User.query.filter_by(id=user_id).all()
        else:
            users = User.query.all()

        users_list = [user.serialize(100) for user in users]
        return jsonify(users=users_list)

    def post(self):
        pass

    def put(self):
        pass

###### Routes
## Post API Routes
api.add_resource(PostAPI, '/api/posts/<nickname>', endpoint='user_posts')
api.add_resource(PostAPI, '/api/posts/', endpoint='all_posts')
api.add_resource(PostAPI, '/api/posts/<int:message_id>', endpoint='delta_posts')

## User API Routes
api.add_resource(UserAPI, '/api/users/<int:user_id>', endpoint='user_info')
api.add_resource(UserAPI, '/api/users/', endpoint='all_user_info')
