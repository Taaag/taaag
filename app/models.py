from datetime import datetime

from app import db
from sqlalchemy import func
from sqlalchemy.orm import aliased


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    name = db.Column(db.String, nullable=False)
    profile_url = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    privacy = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    # tags = db.relationship('Tagging', backref='taggee', foreign_keys='Tagging.taggee_id', lazy='dynamic')
    # tag_others = db.relationship('Tagging', backref='tagger', foreign_keys='Tagging.tagger_id', lazy='dynamic')

    tags = db.relationship('Tag', backref=db.backref('taggees', lazy='dynamic'), secondary='taggings', primaryjoin='Tagging.taggee_id==User.id', lazy='dynamic')
    tag_others = db.relationship('Tag', backref=db.backref('taggers', lazy='dynamic'), secondary='taggings', primaryjoin='Tagging.tagger_id==User.id', lazy='dynamic')

    def get_tags(self):
        return self.tags.with_entities(Tag.name, func.count(Tagging.id)).group_by(Tag.name).all()

    def get_tags_with_tagger(self):
        tagger = aliased(User, name="tagger")
        return self.tags.join(tagger, tagger.id == Tagging.tagger_id).with_entities(Tag.name, tagger).all()

    def insert(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def create(cls, **kwargs):
        user = cls(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    def get_taggees(self):
        return self.taggees.with_entities(User, func.count(Tagging.id)).group_by(User.id).all()

    @classmethod
    def query_tags_by_name(cls, name):
        return cls.query.filter(cls.name.like('%' + name + '%'))

    @classmethod
    def all_tags(cls):
        return cls.query.all()

    @classmethod
    def get_or_create(cls, name):
        tag = cls.query.filter_by(name=name).first()
        if tag is None:
            tag = cls(name=name)
            db.session.add(tag)
            db.session.commit()
        return tag


class Tagging(db.Model):
    __tablename__ = 'taggings'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    tagger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    taggee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)

    db.UniqueConstraint(tagger_id, taggee_id, tag_id)

    # Relationships
    tagger = db.relationship('User', foreign_keys='Tagging.tagger_id')
    taggee = db.relationship('User', foreign_keys='Tagging.taggee_id')
    tag = db.relationship('Tag')

    @classmethod
    def create(cls, **kwargs):
        tagging = cls(**kwargs)
        try:
            db.session.add(tagging)
            db.session.commit()
            return True
        except:
            return False
