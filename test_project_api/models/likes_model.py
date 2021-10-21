from database import db
from sqlalchemy import func, and_
from datetime import timedelta, datetime
from psycopg2 import DataError, ProgrammingError


likes = db.Table(
    "likes",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id")),
    db.Column("event_time", db.DateTime(timezone=False), server_default=func.now())
)


def get_likes_made_per_day(date_from, date_to):
    try:
        likes_per_day = {}

        date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        delta = timedelta(days=1)
        while date_from <= date_to:
            likes_by_day = db.session.query(likes.columns.post_id, func.count(likes.columns.post_id)).where(
                and_(
                    likes.columns.event_time >= date_from.strftime("%Y-%m-%d"),
                    likes.columns.event_time < (date_from + delta).strftime("%Y-%m-%d"))
            ).group_by(likes.columns.post_id).all()

            post_likes_per_day = {}
            for post_likes in likes_by_day:
                post_likes_per_day[f"post_id {post_likes[0]}"] = f"{post_likes[1]} likes"

            likes_per_day[date_from.strftime("%Y-%m-%d")] = post_likes_per_day
            date_from += delta
        return likes_per_day
    except(DataError, ProgrammingError):
        return False
