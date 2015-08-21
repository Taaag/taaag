from datetime import datetime

from app import db
from app.enums import UserPrivacy
from app.utils import is_friend_of
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
    privacy = db.Column(db.Integer, default=UserPrivacy.OPEN, nullable=False)

    # Relationships
    # tags = db.relationship('Tagging', backref='taggee', foreign_keys='Tagging.taggee_id', lazy='dynamic')
    # tag_others = db.relationship('Tagging', backref='tagger', foreign_keys='Tagging.tagger_id', lazy='dynamic')

    tags = db.relationship('Tag', backref=db.backref('taggees', lazy='dynamic'), secondary='taggings', primaryjoin='Tagging.taggee_id==User.id', lazy='dynamic')
    tag_others = db.relationship('Tag', backref=db.backref('taggers', lazy='dynamic'), secondary='taggings', primaryjoin='Tagging.tagger_id==User.id',
                                 lazy='dynamic')

    # def get_tags(self):
    # return self.tags.with_entities(Tag.name, func.count(Tagging.id)).group_by(Tag.name).all()

    def get_tags_with_tagger(self):
        tagger = aliased(User, name="tagger")
        return self.tags.join(tagger, tagger.id == Tagging.tagger_id).with_entities(Tag.name, tagger).all()

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    def allow_tag(self):
        return self.privacy == UserPrivacy.OPEN  # TODO

    def update_privacy(self, privacy):
        if UserPrivacy.is_valid(privacy):
            self.privacy = privacy
            return True
        return False

    def can_tag(self, taggee):
        return is_friend_of(self, taggee) and taggee.allow_tag()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def create(cls, **kwargs):
        user = cls(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_tags_for_user(cls, user_id):
        user = cls.get_by_id(user_id)
        return user.tags.with_entities(Tag.name, func.count(Tagging.id)).group_by(Tag.name).all()

    @classmethod
    def delete_by_uid(cls, user_id):
        user = cls.get_by_id(user_id)
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        return True


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
        name = name.strip().lower()
        if name:
            return cls.query.filter(cls.name.like('%' + name + '%')).all()
        else:
            return None

    @classmethod
    def all_tags(cls):
        return cls.query.all()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name.strip().lower()).first()

    @classmethod
    def get_or_create(cls, name):
        name = name.strip().lower()
        tag = cls.get_by_name(name)
        if tag is None:
            tag = cls(name=name)
            db.session.add(tag)
            db.session.commit()
        return tag

    @classmethod
    def delete_by_name_for_user(cls, name, user):
        name = name.strip().lower()
        tag = cls.get_by_name(name)
        # If the tag does not exist or not belong to the user, indicate error
        if not tag or not tag.taggings.filter_by(taggee_id=user.id).delete():
            return False
        # If nobody has this tag, remove it
        if not tag.taggings.all():
            tag.query.delete()
        # Show success
        db.session.commit()
        return True


class Tagging(db.Model):
    __tablename__ = 'taggings'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    tagger_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    taggee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)

    db.UniqueConstraint(tagger_id, taggee_id, tag_id)

    # Relationships
    tagger = db.relationship('User', foreign_keys='Tagging.tagger_id')
    taggee = db.relationship('User', foreign_keys='Tagging.taggee_id')
    tag = db.relationship('Tag', backref=db.backref('taggings', lazy='dynamic'))

    @classmethod
    def create(cls, **kwargs):
        tagging = cls(**kwargs)
        try:
            db.session.add(tagging)
            db.session.commit()
            return True
        except:
            return False
