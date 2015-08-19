from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    name = db.Column(db.String, nullable=False)
    profile_url = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    privacy = db.Column(db.Integer, nullable=False, default=0)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    @classmethod
    def query_tags_by_name(cls, name):
        return cls.query.filter(cls.name.like('%' + name + '%'))

    @classmethod
    def all_tags(cls):
        cls.query.all()


class Tagging(db.Model):
    __tablename__ = 'taggings'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    tagger = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    taggee = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    tag = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
