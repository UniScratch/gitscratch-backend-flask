from models import *
from flask import Flask, request, g, session
from flask_sqlalchemy import SQLAlchemy
import uuid
import time


app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


@app.route("/")
def index():
    if g.user:
        return g.user.name
    else:
        return "Hello, World!"


@app.before_request
def load_logged_in_user():
    _session = session.get("session")
    if(_session is not None):
        user = User.query.filter_by(
            _session=_session).first()
        if (time.time() - user._session_time < 60*60):  # 1 hr
            user._session_time = int(time.time())
            db.session.commit()
            g.user = user
        else:
            g.user = None
    else:
        g.user = None


@app.route("/auth/captcha", methods=["GET"])
def auth_captcha():
    return "captcha"


@app.route("/auth/register", methods=["POST"])
def auth_register():
    email = request.json['email']
    name = request.json['username']
    password = request.json['password']
    if db.session.query(
        User.query.filter_by(email=email).exists()
    ).scalar():
        return {'message': "Email already exists"}, 500
    db.session.add(User(
        email=email,
        name=name,
        password=password,
        created_at=int(time.time())))
    db.session.commit()
    return {}


@app.route("/auth/login", methods=["POST"])
def auth_login():
    email = request.json['email']
    password = request.json['password']
    user = db.session.query(User).filter_by(email=email).first()
    if not user or user.password != password:
        return {'message': "Invalid username or password"}, 500
    _uuid = str(uuid.uuid4())
    user._session = _uuid
    user._session_time = int(time.time())
    db.session.commit()
    session['session'] = _uuid
    # session will be stored in client cookie
    return {}


@app.route("/auth/session", methods=["GET"])
def auth_session():
    if g.user:
        return {'data': g.user.to_json()}
    else:
        return {'message': "Unauthorized"}, 500


if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")
