# from sqlalchemy import db.Column, ForeignKey, db.Integer, db.String
# from sqlalchemy.orm import relationship
from main import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    follower = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    website = db.Column(db.String, default="")
    bio = db.Column(db.String, default="")
    avatar = db.Column(db.String, default="")
    level = db.Column(db.Integer, default=0)
    exp= db.Column(db.Integer, default=0)
    verified = db.Column(db.Integer, default=0)
    muted=db.Column(db.Integer, default=0)
    banned=db.Column(db.Integer, default=0)
    password = db.Column(db.String)
    readme=db.Column(db.String, default="")
    created_at = db.Column(db.Integer)
    _session = db.Column(db.String)
    _session_time = db.Column(db.Integer)
    # projects = db.Column(db.ForeignKey(Project.))

    def to_json(self):
        if hasattr(self, '__table__'):
            json={i.name: getattr(self, i.name) for i in self.__table__.columns}
            del json['password']
            del json['_session']
            del json['_session_time']
            return json
        raise AssertionError(
            '<%r> does not have attribute for __table__' % self)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String, index=True)
    description = db.Column(db.String, index=True)
    # owner_id = db.Column(db.Integer, ForeignKey("users.id"))

    # author = relationship("User", back_populates="projects")


db.create_all()
