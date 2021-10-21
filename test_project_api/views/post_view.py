from flask import Blueprint, request, make_response
from flask.views import MethodView
from test_project_api.models.post_model import Post
from test_project_api.models.user_model import User
from check_for_jwt_token import token_required

mod = Blueprint('post', __name__, static_folder="static", template_folder="templates")


class PostView(MethodView):
    @token_required
    def post(self, post_request, user_id):
        user = User.get_by_id(user_id)
        if user:
            user.update_last_request_time()
            data = request.get_json()
            text = data.get("text")
            if text:
                Post.create(text, user_id)
                return make_response("Post created successfully", 200)
            return make_response("Can not create a post", 400)


class LikePostView(MethodView):
    @token_required
    def post(self, post_request, user_id, post_id):
        user = User.get_by_id(user_id)
        if user:
            user.update_last_request_time()
            like_post = user.like_post(post_id)
            if like_post:
                return make_response("Post liked successfully", 200)
            return make_response("Post is already liked or an error occurred!", 200)
        return make_response("Can not like a post", 400)


class UnlikePostView(MethodView):
    @token_required
    def post(self, post_request, user_id, post_id):
        user = User.get_by_id(user_id)
        if user:
            user.update_last_request_time()
            unlike_post = user.unlike_post(post_id)
            if unlike_post:
                return make_response("Post unliked successfully", 200)
            return make_response("Post is not liked or an error occurred!", 200)
        return make_response("Can not unlike a post", 400)


post_view = PostView.as_view('post')
mod.add_url_rule('/<user_id>/create_post', view_func=post_view, methods=['POST'])

post_like_view = LikePostView.as_view('like_post')
mod.add_url_rule('/<user_id>/like_post/<post_id>', view_func=post_like_view, methods=['POST'])

post_unlike_view = UnlikePostView.as_view('unlike_post')
mod.add_url_rule('/<user_id>/unlike_post/<post_id>', view_func=post_unlike_view, methods=['POST'])
