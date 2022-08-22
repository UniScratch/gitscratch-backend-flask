# from sqlalchemy import db.Column, ForeignKey, db.Integer, db.String
# from sqlalchemy.orm import relationship
import json
from email.policy import default

import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

from gitscratch_init import db


class Captcha(db.Model):
    __tablename__ = "captchas"

    uuid = db.Column(db.String, primary_key=True)
    id = db.Column(db.Integer)
    created_at = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    tag = db.Column(db.String, default="")
    tag_color = db.Column(db.String, default="#2196F3")
    follower = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    website = db.Column(db.String, default="")
    bio = db.Column(db.String, default="")
    avatar = db.Column(
        db.String, default="")
    level = db.Column(db.Integer, default=0)
    exp = db.Column(db.Integer, default=0)
    verified = db.Column(db.Integer, default=0)
    muted = db.Column(db.Integer, default=0)
    banned = db.Column(db.Integer, default=0)
    permission = db.Column(db.String, default='user')
    _password = db.Column(db.String)
    readme = db.Column(db.String, default="")
    created_at = db.Column(db.Integer)
    _session = db.Column(db.String)
    _session_time = db.Column(db.Integer)
    # projects = db.Column(db.ForeignKey(Project.))

    def to_json(self):
        """Return user info as json."""
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_password']
            del json['_session']
            del json['_session_time']
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)

    @hybrid_property
    def password(self):
        """Return the password."""
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = bcrypt.hashpw(
            value.encode(), bcrypt.gensalt()).decode()

    def checkPassword(self, value):
        """Check the password against the stored hash."""
        return bcrypt.checkpw(value.encode(), self._password.encode())


class Commit(db.Model):
    __tablename__ = "commits"

    id = db.Column(db.Integer, primary_key=True, index=True)
    hash = db.Column(db.String, index=True)
    message = db.Column(db.String, default="Init")
    time = db.Column(db.Integer)
    type = db.Column(db.String, default="commit")  # autosave, commit
    thumbnail = db.Column(db.String, default="")
    _parents = db.Column(db.String, default="[]")
    _project_id = db.Column(db.Integer)
    _author = db.Column(db.Integer)

    @hybrid_property
    def author(self):
        return User.query.filter_by(id=self._author).first()

    @hybrid_property
    def parents(self):
        return json.loads(self._parents)

    @hybrid_property
    def project(self):
        return Project.query.filter_by(id=self._project_id).first()

    def to_json(self, project=False):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_author']
            json["author"] = self.author.to_json()
            del json['_project_id']
            if(project):
                json["project"] = self.project.to_json()
            del json['_parents']
            json["parents"] = self.parents
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String, index=True, default='未命名作品')
    readme = db.Column(db.String, index=True, default='')
    public = db.Column(db.Integer, default=0)  # 0: private, 1: public
    source = db.Column(db.Integer, default=0)  # 0: open, 1: readonly, 2: close
    # 0: normal, 1: deleted, 2: archived
    status = db.Column(db.Integer, default=0)
    _author = db.Column(db.Integer)  # user id
    _head = db.Column(db.String)  # commit hash

    @hybrid_property
    def author(self):
        return User.query.filter_by(id=self._author).first()

    @hybrid_property
    def like(self):
        return User_Operation.query.filter_by(_target_type="project", _target_id=self.id, type="project.like").count()

    def is_liked(self, user=None):
        if user is None:
            return False
        return User_Operation.query.filter_by(_target_type="project", _target_id=self.id, type="project.like", _user=user.id).count() > 0

    @hybrid_property
    def star(self):
        return User_Operation.query.filter_by(_target_type="project", _target_id=self.id, type="project.star").count()

    def is_starred(self, user=None):
        if user is None:
            return False
        return User_Operation.query.filter_by(_target_type="project", _target_id=self.id, type="project.star", _user=user.id).count() > 0

    @hybrid_property
    def view(self):
        return User_Operation.query.filter_by(_target_type="project", _target_id=self.id, type="project.view").count()

    def is_viewed(self, user=None):
        if user is None:
            return False
        return User_Operation.query.filter_by(_target_type="project", _target_id=self.id, type="project.view", _user=user.id).count() > 0

    @hybrid_property
    def head(self):
        return Commit.query.filter_by(hash=self._head, _project_id=self.id).first()

    @hybrid_property
    def totalCommits(self):
        return Commit.query.filter_by(_project_id=self.id).count()

    def to_json(self, user=None):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_author']
            json["author"] = self.author.to_json()
            json['like'] = self.like
            json['star'] = self.star
            json['view'] = self.view
            json['is_liked'] = self.is_liked(user)
            json['is_starred'] = self.is_starred(user)
            json['is_viewed'] = self.is_viewed(user)
            json['totalCommits'] = self.totalCommits
            del json['_head']
            json["head"] = self.head.to_json(project=False)
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String, default="")
    content = db.Column(db.String, default="")
    status = db.Column(db.Integer, default=0)  # 0: private, 1: public
    _user = db.Column(db.Integer)  # user id
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)

    @hybrid_property
    def user(self):
        return User.query.filter_by(id=self._user).first().to_json()

    def to_json(self):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_user']
            json["user"] = self.user
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)


class User_Operation(db.Model):
    __tablename__ = "user_operations"

    id = db.Column(db.Integer, primary_key=True, index=True)
    # project.star, project.like, project.view, user.signin, etc.
    type = db.Column(db.String)
    _target_type = db.Column(db.String)  # project, user
    _target_id = db.Column(db.Integer)
    _user = db.Column(db.Integer)  # user id
    created_at = db.Column(db.Integer)

    @hybrid_property
    def target(self):
        if(self._target_type == "project"):
            return Project.query.filter_by(id=self._target_id).first().to_json()
        elif(self._target_type == "user"):
            return User.query.filter_by(id=self._target_id).first().to_json()
        else:
            return None

    @hybrid_property
    def user(self):
        return User.query.filter_by(id=self._user).first().to_json()

    def to_json(self):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_target_type']
            del json['_target_id']
            del json['_user']
            json["target"] = self.target
            json["user"] = self.user
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, index=True)
    comment = db.Column(db.String)
    page_id = db.Column(db.Integer)
    target_type = db.Column(db.String)  # project or user
    target_id = db.Column(db.Integer)  # project id or user id
    _reply = db.Column(db.Integer, default=0)  # comment id
    _user = db.Column(db.Integer)  # user id
    time = db.Column(db.Integer)
    region = db.Column(db.String, default="未知")
    _ip = db.Column(db.String, default="未知")
    status = db.Column(db.Integer, default=0)  # 0: normal 1: deleted 2: hidden

    @hybrid_property
    def user(self):
        return User.query.filter_by(id=self._user).first().to_json()

    @hybrid_property
    def target(self):
        if(self.target_type == "project"):
            return Project.query.filter_by(id=self.target_id).first().to_json()
        elif(self.target_type == "user"):
            return User.query.filter_by(id=self.target_id).first().to_json()
        else:
            return None

    @hybrid_property
    def reply(self):
        if(self._reply == 0):
            return None
        else:
            return Comment.query.filter_by(id=self._reply).first().to_json(with_reply=False)

    def to_json(self, with_reply=True):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_user']
            del json['_ip']
            del json['_reply']
            json["user"] = self.user
            json["target"] = self.target
            if(with_reply):
                json["reply"] = self.reply
            else:
                json['reply'] = None
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True, index=True)
    comment = db.Column(db.String)
    target_type = db.Column(db.String)  # project or user
    target_id = db.Column(db.Integer)  # project id or user id
    _user = db.Column(db.Integer)  # user id
    time = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)  # 0: normal 1: deleted 2: hidden

    @hybrid_property
    def user(self):
        return User.query.filter_by(id=self._user).first().to_json()

    def to_json(self):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_user']
            json["user"] = self.user
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)


db.create_all()
