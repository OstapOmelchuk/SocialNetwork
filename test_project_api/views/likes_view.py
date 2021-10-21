from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView
from test_project_api.models.likes_model import get_likes_made_per_day


mod = Blueprint('like', __name__, static_folder="static", template_folder="templates")


class LikesView(MethodView):
    def get(self):
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        likes_per_days = get_likes_made_per_day(date_from, date_to)
        if likes_per_days:
            return make_response(jsonify(likes_per_days), 200)
        return make_response("no likes were made during these days or an error occurred", 400)


likes_view = LikesView.as_view('likes')
mod.add_url_rule('/', view_func=likes_view, methods=['GET'])
