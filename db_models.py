from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import CheckConstraint
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    profile_pic = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(300))
    address = db.Column(db.String(300))
    photos = db.Column(db.String(3000))
    ratings = db.Column(db.String(300))
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cleanliness = db.Column(db.Integer)
    facilities = db.Column(db.Integer)
    accessibility = db.Column(db.Integer)
    natural_diversity = db.Column(db.Integer)
    eco_friendly_practices = db.Column(db.Integer)
    safety_security = db.Column(db.Integer)
    recreational_opportunities = db.Column(db.Integer)
    community_engagement = db.Column(db.Integer)
    educational_value = db.Column(db.Integer)
    scenic_beauty = db.Column(db.Integer)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_name = db.Column(db.Integer, db.ForeignKey('user.username'), nullable=False)
    text = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(300))
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship to Space model (assuming one-to-many)
    space = db.relationship('Space', backref=db.backref('community', uselist=False, lazy=True))

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    text = db.Column(db.String(1000))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=True)
    community = db.relationship('Community', backref=db.backref('posts', lazy=True))
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    replies = db.relationship('CommunityPost', backref=db.backref('reply_to', remote_side=[id]), lazy=True)

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50))  # e.g., 'member', 'moderator'
    community = db.relationship('Community', backref=db.backref('memberships', lazy=True))
    user = db.relationship('User', backref=db.backref('memberships', lazy=True))


