from datetime import datetime

from app import db

from sqlalchemy.dialects.mysql import BIGINT, SMALLINT


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(BIGINT(unsigned=True), nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    name = db.Column(db.String, nullable=False)
    profile_url = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    privacy = db.Column(SMALLINT, default=0, nullable=False)

    # Relationships
    tags = db.relationship('Tagging', backref='taggee', foreign_keys='Tagging.taggee_id', lazy='dynamic')
    tag_others = db.relationship('Tagging', backref='tagger', foreign_keys='Tagging.tagger_id', lazy='dynamic')


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    name = db.Column(db.String, nullable=False, unique=True)

    # Relationships
    taggings = db.relationship('Tagging', backref='tag', lazy='dynamic')

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

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    tagger_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('users.id'), nullable=False)
    taggee_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('users.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
