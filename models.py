# from sqlalchemy import db.Column, ForeignKey, db.Integer, db.String
# from sqlalchemy.orm import relationship
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
    follower = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    website = db.Column(db.String, default="")
    bio = db.Column(db.String, default="")
    avatar = db.Column(
        db.String, default="/GitScratch-icon-background-blue.svg")
    level = db.Column(db.Integer, default=0)
    exp = db.Column(db.Integer, default=0)
    verified = db.Column(db.Integer, default=0)
    muted = db.Column(db.Integer, default=0)
    banned = db.Column(db.Integer, default=0)
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
        self._password = bcrypt.hashpw(value.encode(), bcrypt.gensalt()).decode()
    
    def checkPassword(self, value):
        """Check the password against the stored hash."""
        return bcrypt.checkpw(value.encode(), self._password.encode())


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String, index=True)
    readme = db.Column(db.String, index=True)
    _author = db.Column(db.Integer) # user id
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)

    @hybrid_property
    def author(self):
        return User.query.filter_by(id=self._author).first().to_json()

    def to_json(self):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_author']
            json["author"] = self.author
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)

class Project_User_Operation(db.Model):
    __tablename__ = "project_user_operations"

    id = db.Column(db.Integer, primary_key=True, index=True)
    type=db.Column(db.String) # star, like
    _project = db.Column(db.Integer) # project id
    _user = db.Column(db.Integer) # user id
    created_at = db.Column(db.Integer)

    @hybrid_property
    def project(self):
        return Project.query.filter_by(id=self._project).first().to_json()

    @hybrid_property
    def user(self):
        return User.query.filter_by(id=self._user).first().to_json()

    def to_json(self):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_project']
            del json['_user']
            json["project"] = self.project
            json["user"] = self.user
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)

class Comment(db.Model):
    __tablename__ = "comments"

    id=db.Column(db.Integer, primary_key=True, index=True)
    comment=db.Column(db.String)
    target_type=db.Column(db.String) # project or user
    target_id=db.Column(db.Integer) # project id or user id
    _user=db.Column(db.Integer) # user id
    time=db.Column(db.Integer)
    region=db.Column(db.String, default="未知")
    _ip=db.Column(db.String, default="未知")
    status=db.Column(db.Integer, default=0) # 0: normal 1: deleted 2: hidden

    @hybrid_property
    def user(self):
        return User.query.filter_by(id=self._user).first().to_json()

    def to_json(self):
        if hasattr(self, '__table__'):
            json = {i.name: getattr(self, i.name)
                    for i in self.__table__.columns}
            del json['_user']
            del json['_ip']
            json["user"]=self.user
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
