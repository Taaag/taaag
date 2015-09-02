from datetime import datetime

from app import db
from app.enums import UserPrivacy
from app.utils import is_friend_of, get_user_friends, has_friends_permission
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError
from datetime import timezone


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

    tags = db.relationship('Tag', backref=db.backref('taggees', lazy='dynamic'), secondary='taggings',
                           primaryjoin='Tagging.taggee_id==User.id', lazy='dynamic')
    tag_others = db.relationship('Tag', backref=db.backref('taggers', lazy='dynamic'), secondary='taggings',
                                 primaryjoin='Tagging.tagger_id==User.id', lazy='dynamic')

    likees = db.relationship('User', backref=db.backref('likers', lazy='dynamic'), secondary='likings',
                             primaryjoin='Liking.liker_id==User.id', secondaryjoin="User.id==Liking.likee_id",
                             lazy='dynamic')

    # def get_tags(self):
    # return self.tags.with_entities(Tag.name, func.count(Tagging.id)).group_by(Tag.name).all()

    def friends_api_authorized(self):
        return has_friends_permission(self)

    def get_friends(self):
        return [_ for _ in get_user_friends(self) if User.get_by_id(_['id'])]

    def is_friend_of(self, other_id):
        return User.get_by_id(other_id) and is_friend_of(self, other_id)

    def get_tags_with_tagger(self):
        tagger = aliased(User, name="tagger")
        return self.tags.join(tagger, tagger.id == Tagging.tagger_id).order_by(Tagging.created).with_entities(
            Tag.name, tagger).all()

    def get_tags_order_by_time(self):
        return self.tags.with_entities(Tag.name, func.min(Tagging.created).label('first')).group_by(Tag.name). \
            order_by('first desc').all()

    def to_dict(self):
        return {'id': str(self.id), 'name': self.name}

    def allow_tag(self):
        return self.privacy == UserPrivacy.OPEN  # TODO

    def update_privacy(self, privacy):
        if UserPrivacy.is_valid(privacy):
            self.privacy = privacy
            return True
        return False

    def can_tag(self, taggee):
        return is_friend_of(self, taggee.id) and taggee.allow_tag()

    def update(self):
        db.session.commit()

    def is_liking(self, likee):
        result = Liking.get_by_liker_likee(likee)
        if not result:
            return False
        return result[0].event_id

    def like(self, likee, event_id):
        return Liking.create(liker=self, likee=likee, event_id=event_id)

    def unlike(self, likee):
        return Liking.delete_by_liker_likee(self, likee)

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
        taggees = self.taggees.with_entities(User, func.count(Tagging.id).label('votes')). \
            group_by(User.id).order_by('votes DESC').all()
        if not taggees:
            db.session.delete(self)
            db.session.commit()
        return taggees

    def get_taggees_filtered(self, friends_list):
        taggees = self.taggees.filter(User.id.in_(friends_list)). \
            with_entities(User, func.count(Tagging.id).label('votes')). \
            group_by(User.id).order_by('votes DESC').all()
        return taggees

    @classmethod
    def query_tags_by_name(cls, name):
        name = name.strip().lower()
        if name:
            return cls.query.filter(cls.name.like(name + '%')).order_by(cls.name).all() + \
                   cls.query.filter(cls.name.like('% ' + name + '%')).order_by(cls.name).all()
        else:
            return None

    @classmethod
    def query_tags_by_name_filtered(cls, name, friends_list):
        name = name.strip().lower()
        if name:
            return cls.query.filter(cls.name.like('%' + name + '%')).join(Tagging, Tagging.tag_id == Tag.id). \
                filter(Tagging.taggee_id.in_(friends_list)).all()
        else:
            return None

    @classmethod
    def all_tags_filtered(cls, friends_list):
        return [_[1] for _ in
                db.session.query(Tagging.tag_id, Tag.name).filter(Tagging.taggee_id.in_(friends_list)).group_by(
                    Tagging.tag_id).join(cls,
                                         Tagging.tag_id == Tag.id).all()]

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
        tag.get_taggees()
        # Show success
        db.session.commit()
        return True

    @classmethod
    def get_by_tagger_and_taggee(cls, tagger_id, taggee_id):
        return cls.query.join(Tagging, Tagging.tag_id == Tag.id).filter(Tagging.tagger_id == tagger_id). \
            filter(Tagging.taggee_id == taggee_id).with_entities(Tag.name).all()


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
        except IntegrityError:
            db.session.rollback()
            raise


class Liking(db.Model):
    __tablename__ = 'likings'

    created = db.Column(db.DateTime, default=datetime.utcnow().replace(tzinfo=timezone.utc), nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)

    liker_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False, primary_key=True)
    likee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False, primary_key=True)
    event_id = db.Column(db.String, nullable=False, unique=True)

    # Relationships
    liker = db.relationship('User', foreign_keys='Liking.liker_id')
    likee = db.relationship('User', foreign_keys='Liking.likee_id')

    @classmethod
    def create(cls, **kwargs):
        liking = cls(**kwargs)
        try:
            db.session.add(liking)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise

    @classmethod
    def delete_by_liker_likee(cls, liker, likee):
        result = cls.get_by_liker_likee(liker, likee)
        if result:
            db.session.delete(result)
            db.session.commit()
            return True
        return False

    @classmethod
    def get_by_liker_likee(cls, liker, likee):
        return cls.query().filter(liker_id=liker.id, likee_id=likee.id).all()
