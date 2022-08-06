import time
import uuid

from flask import g, request
from flask import json
from werkzeug.exceptions import HTTPException

from models import *
from captcha import captcha

from gitscratch_init import app, db


def error(message="Unknown error"):
    return json.dumps(
        {"status": "error",
         "message": message}
    )


def success(data=None):
    return json.dumps(
        {"status": "success",
         "data": data}
    )


@app.route("/")
def index():
    """For test only"""
    if g.user:
        return g.user.name
    else:
        return success()


@app.before_request
def load_logged_in_user():
    """Check if user is logged in"""
    if 'X-Gitscratch-Session' in request.headers:
        _session = request.headers['X-Gitscratch-Session']
    else:
        _session = None
    if _session is not None:  # if headers has session
        user = User.query.filter_by(_session=_session).first()
        if user is not None:  # if session is valid
            if time.time() - user._session_time <= 60 * 60:  # 1 hour
                user._session_time = int(time.time())
                db.session.commit()
                g.user = user
            else:  # session expired
                g.user = None
        else:  # if session is invalid
            g.user = None
    else:  # if headers has no session
        g.user = None


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON for HTTP errors. Only available for production environment."""
    return error(str(e.code) + " " + e.name)


@app.route("/auth/captcha", methods=["GET"])
def auth_captcha():
    """Get captcha image"""
    _captcha = captcha.getCaptcha()
    _uuid = str(uuid.uuid4())
    db.session.add(Captcha(
        uuid=_uuid,
        id=_captcha['id'],
        created_at=int(time.time())))
    db.session.commit()
    # print(_captcha)
    return success(
        {
            "captcha_uuid": _uuid,
            "captcha_base64": _captcha['base64']
        }
    )
    # return error()


@app.route("/auth/register", methods=["POST"])
def auth_register():
    """Register new user"""
    email = request.json['email']
    name = request.json['username']
    password = request.json['password']
    captcha_uuid = request.json['captcha_uuid']
    captcha_value = request.json['captcha_value']
    _captcha = db.session.query(Captcha).filter_by(uuid=captcha_uuid).first()
    if (not _captcha) or (not captcha.checkCaptcha(_captcha.id, captcha_value)) or (time.time() - _captcha.created_at > 15*60):  # 15min
        return error("Invalid captcha")
    if db.session.query(
        User.query.filter_by(email=email).exists()
    ).scalar():
        return error("Email already exists")
    db.session.add(User(
        email=email,
        name=name,
        password=password,
        created_at=int(time.time())))
    db.session.commit()
    return success()


@app.route("/auth/login", methods=["POST"])
def auth_login():
    """Login user"""
    email = request.json['email']
    password = request.json['password']
    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.checkPassword(password):
        return error("Invalid username or password")
    _uuid = str(uuid.uuid4())
    user._session = _uuid
    user._session_time = int(time.time())
    db.session.commit()
    # session['session'] = _uuid
    return success({'session': _uuid})


@app.route("/auth/session", methods=["GET"])
def auth_session():
    """Get user session"""
    if g.user:
        return success({'data': g.user.to_json()})
    else:
        return error("Unauthorized")


@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    """Logout user"""
    if g.user:
        g.user._session = ""
        g.user._session_time = 0
        db.session.commit()
        return success()
    else:
        return error("Unauthorized")


@app.route("/users/<id>/info", methods=["GET"])
def users_info(id):
    """Get user info"""
    user = db.session.query(User).filter_by(id=id).first()
    if not user:
        return error("Invalid id")
    return success(user.to_json())


@app.route("/users/<id>/info", methods=["POST"])
def users_info_update(id):
    """Update user info"""
    user = db.session.query(User).filter_by(id=id).first()
    if not user or g.user == None:
        return error("Invalid id")
    elif(user.id == g.user.id):
        # user.name = request.json['username']
        # user.email = request.json['email']
        # user.password = request.json['password']
        db.session.commit()
        return success()
    return success(user.to_json())

@app.route("/users/<id>/profile", methods=["POST"])
def users_info_update(id):
    """Update user's profile"""
    user = db.session.query(User).filter_by(id=id).first()
    if not user or g.user == None:
        return error("Invalid id")
    elif(user.id == g.user.id):
        user.bio = request.json['bio']
        user.website = request.json['website']
        user.readme = request.json['readme']
        db.session.commit()
        return success()
    return success(user.to_json())

@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Method"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Server"] = "Python with Super Cow Powers"
    return response


if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")
