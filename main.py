from base64 import decode
import math
import time
import uuid
import hashlib

from flask import g, request
from flask import json
from werkzeug.exceptions import HTTPException
from PIL import Image
import geoip2.database

from models import *
from captcha import captcha

from gitscratch_init import app, db

geoip2reader = geoip2.database.Reader(
    'geolite2/GeoLite2-City.mmdb')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def error(message="Unknown error"):
    return json.dumps(
        {"status": "error",
         "message": message}
    ), 500


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
    # print(request.headers)
    if ('X-Real-IP' in request.headers):
        g.ip = request.headers['X-Real-IP']
    else:
        g.ip = request.remote_addr
    try:
        region = geoip2reader.city(g.ip)
        g.ip_region = region.country.names['zh-CN']+" " + \
            region.subdivisions.most_specific.names['zh-CN']
        # +region.city.names['zh-CN']
    except:
        g.ip_region = '未知'
    # print(g.ip_region)
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
        if 'name' in request.json:
            user.name = request.json['name']
        if 'email' in request.json:
            user.email = request.json['email']
        if 'website' in request.json:
            user.website = request.json['website']
        if 'bio' in request.json:
            user.bio = request.json['bio']
        if 'avatar' in request.json:
            user.avatar = request.json['avatar']
        if 'readme' in request.json:
            user.readme = request.json['readme']
        db.session.commit()
        return success()
    return error("Unauthorized")


def getProjects(target_id, args):
    query = db.session.query(Project).filter_by(_author=target_id).order_by(
        Project.created_at)
    projects = query.all()
    _projects = [comment.to_json() for comment in projects]
    # print(time.time()-startTime)
    return success({'projects': _projects, 'totalProjects': query.count()})

@app.route("/users/<id>/projects", methods=["GET"])
def users_projects(id):
    """Get user projects"""
    return getProjects(target_id=id, args=request.args)

# @app.route("/users/<id>/profile", methods=["POST"])
# def users_info_update(id):
#     """Update user's profile"""
#     user = db.session.query(User).filter_by(id=id).first()
#     if not user or g.user == None:
#         return error("Invalid id")
#     elif(user.id == g.user.id):
#         user.bio = request.json['bio']
#         user.website = request.json['website']
#         user.readme = request.json['readme']
#         db.session.commit()
#         return success()
#     return success(user.to_json())

# app.route("/users/<id>/avatar", methods=["POST"])
# def users_info_update(id):
#     """Update user's avatar"""
#     user = db.session.query(User).filter_by(id=id).first()
#     if not user or g.user == None:
#         return error("Invalid id")
#     elif(user.id == g.user.id):
#         files = request.files['avatar']
#         size = (256,256)
#         im = Image.open(avatar)
#         im.thumbnail(size)
#         if avatar and allow_file(avatar.filename):
#             try:
#                 #file.save(os.path.join("./static/uploads/",avatar.filename))
#                 #user.avatar=os.path.join("./static/uploads/",avatar.filename)
#                 db.session.commit()
#             except:
#                 return error("Failed to save the picture")
#         else:
#             return error("Unsafe file type")
#         return success()
#     return success(user.to_json())

# --------------------------


@app.route("/projects/<id>/info", methods=["GET"])
def projects_info(id):
    """Get project info"""
    project = db.session.query(Project).filter_by(id=id).first()
    if not project:
        return error("Invalid id")
    return success(project.to_json())


@app.route("/projects/<id>/info", methods=["POST"])
def projects_info_update(id):
    """Update project info"""
    project = db.session.query(Project).filter_by(id=id).first()
    if not project or g.user == None:
        return error("Invalid id")
    elif(project.id == g.user.id):
        if 'title' in request.json:
            project.title = request.json['title']
        if 'readme' in request.json:
            project.readme = request.json['readme']
        if 'source' in request.json:
            project.source = request.json['source']
        if 'public' in request.json:
            project.public = request.json['public']
        if 'status' in request.json:
            project.status = request.json['status']
        db.session.commit()
        return success()
    return error("Unauthorized")

def getComments(target_type, target_id, args):
    pageSize = 10  # once this value is changed, the database should be reset
    query = db.session.query(Comment).filter_by(target_type=target_type, target_id=target_id).order_by(
        Comment.time)
    pageId = int(args['pageId']
                 ) if 'pageId' in args else query.paginate(per_page=10, error_out=False).pages
    pagination = query.paginate(page=pageId, per_page=10, error_out=False)
    comments = pagination.items
    _comments = [comment.to_json() for comment in comments]
    # print(time.time()-startTime)
    return success({'comments': _comments, 'pageId': pageId, 'pageSize': pageSize, 'totalPages': pagination.pages, 'totalComments': query.count()})


def newComment(target_type, target_id, request_json):
    if(g.user == None):
        return error("Unauthorized")
    db.session.add(Comment(
        comment=request_json['comment'],
        page_id=db.session.query(Comment).filter_by(target_type=target_type, target_id=target_id).order_by(
            Comment.time).count()//10+1,
        target_type=target_type,
        target_id=target_id,
        _reply=request_json['reply'] if 'reply' in request_json else 0,
        _user=g.user.id,
        time=int(time.time()),
        region=g.ip_region,
        _ip=g.ip
    ))
    db.session.commit()
    return success()


def updateComment(target_type, target_id, request_json):
    user = db.session.query(User).filter_by(id=target_id).first()
    if not user or g.user == None:
        return error("Invalid id")
    elif(user.id == g.user.id):
        comment_id = request_json['id']
        comment = db.session.query(Comment).filter_by(id=comment_id).first()
        if not comment:
            return error("Invalid comment id")
        else:
            if('comment' in request_json):
                comment.comment = request_json['comment']
            if('status' in request_json):
                comment.status = request_json['status']
            db.session.commit()
            return success()
    return error("Unauthorized")


@app.route("/users/<id>/comments", methods=["GET"])
def users_comments(id):
    """Get user comments"""
    return getComments(target_type="user", target_id=id, args=request.args)


@app.route("/users/<id>/comments/new", methods=["POST"])
def users_comments_new(id):
    """Create new comment"""
    return newComment(target_type='user', target_id=id, request_json=request.json)


@app.route("/users/<id>/comments", methods=["POST"])
def users_comments_update(id):
    """Update comment"""
    return updateComment(target_type='user', target_id=id, request_json=request.json)


@app.route("/projects/<id>/comments", methods=["GET"])
def projects_comments(id):
    """Get project comments"""
    return getComments(target_type="project", target_id=id, args=request.args)


@app.route("/projects/<id>/comments/new", methods=["POST"])
def projects_comments_new(id):
    """Create new comment"""
    return newComment(target_type='project', target_id=id, request_json=request.json)


@app.route("/projects/<id>/comments", methods=["POST"])
def projects_comments_update(id):
    """Update comment"""
    return updateComment(target_type='project', target_id=id, request_json=request.json)


@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Method"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Server"] = "Python with Super Cow Powers"
    if (g.user == None):
        response.headers['X-GitScratch-User'] = 'None'
    return response


if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")
