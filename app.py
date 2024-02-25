from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class User(db.Model()):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30))
    email = db.Column(db.String(30))
    password = db.Column(db.String(256))

class Profile(db.Model()):
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, db.foreign_key(User.id))
    country = db.Column(db.String(20))
    languages = db.Column(db.String(200))
    birthDate = db.Column(db.Date)
    about = db.Columnn(db.Text)

USERNAME_PATTERN = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-"
EMAIL_PATTERN = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-@"

@app.route("/register", methods = ["POST"])
def register():
    try:
        username = request.json["username"]
        email = request.json["email"]
        password = request.json["password"]
        rpassword = request.json["repeat_password"]
    except:
        abort(400)
    
    if len(username) > 30 or len(username) < 1:
        return {"Status" : "Failure", "Response" : "Invalid username length"}
    for i in username:
        if i not in USERNAME_PATTERN:
            return {"Status" : "Failure", "Response" : "Invalid username"}
        
    if len(email) > 30 or len(email) < 1:
        return {"Status" : "Failure", "Response" : "Invalid email length"}
    for i in email:
        if i not in EMAIL_PATTERN:
            return {"Status" : "Failure", "Response" : "Invalid email"}
    if "@" not in email:
        return {"Status" : "Failure", "Response" : "Invalid email"}
    
    if password != rpassword:
        return {"Status" : "Failure", "Response" : "Passwords don't lol-match (hehe)"}
    
    hpw = generate_password_hash(password)

    newUser = User(username = username, email = email, password = hpw)
    db.session.add(newUser)
    db.session.commit()

    return {"Status" : "Success", "Response" : "User registered", "ID" : newUser.id}

@app.route("/login", methods = ["POST"])
def login():
    try:
        email = request.json["email"]
        password = request.json["password"]
    except:
        abort(400)

    if len(email) > 30 or len(email) < 1:
        return {"Status" : "Failure", "Response" : "Invalid email length"}
    for i in email:
        if i not in EMAIL_PATTERN:
            return {"Status" : "Failure", "Response" : "Invalid email"}
    if "@" not in email:
        return {"Status" : "Failure", "Response" : "Invalid email"}

    user = User.query.filter_by(email = email)
    if not user:
        return {"Status" : "Failure", "Response" : "User not found"}

    
    if not check_password_hash(user.password, password):
        return {"Status" : "Failure", "Response" : "Wrong password"}

    return {"Status" : "Success", "Response" : "User logged in", "ID" : user.id}

COUNTRY_LANGUAGE_PATTERN = "abcdefhijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -"
ABOUT_PATTERN = "abcdefhijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -().,;\"'!?"

@app.route("/profile", methods = ["POST", "GET"])
def profile():
    if request.method == "POST":
        try:
            userId = request.json["userId"]
            country = request.json["country"]
            languages = request.json["languages"]
            birthDate = request.json["birthDate"]
            about = request.json["about"]
        except:
            abort(400)

        if type(userId) != int:
            return {"Status" : "Failure", "Response" : "Invalid user ID"}
        if not User.query.filter_by(id = userId):
            return {"Status" : "Failure", "Response" : "User does not exist"}
        
        suppProfile = Profile.query.filter_by(userId = user.id)
        if suppProfile:
            db.session.delete(suppProfile)
            db.session.commit()

        if len(country) > 30:
            return {"Status" : "Failure", "Response" : "Invalid country name length"}
        for i in country:
            if i not in COUNTRY_LANGUAGE_PATTERN:
                return {"Status" : "Failure", "Response" : "Invalid country name"}
            
        if len("".join(languages)) > 200:
            return {"Status" : "Failure", "Response" : "Invalid lanuage array length"}
        for l in languages:
            for i in l:
                if i not in COUNTRY_LANGUAGE_PATTERN:
                    return {"Status" : "Failure", "Response" : "Invalid language name"}

        try:
            datetime.date.fromisoformat(birthDate)
        except ValueError:
            return {"Status" : "Failure", "Response" : "Invalid date format"}
        
        for i in about:
            if i not in ABOUT_PATTERN:
                return {"Status" : "Failure", "Response" : "Invalid about section"}
        
        newProfile = Profile(userId = userId, country = country, languges = "".join(languages), birthDate = datetime.strptime(birthDate, "%Y-%m-%d"), about = about)
        db.session.add(newProfile)
        db.session.commit()

        return {"Status" : "Success", "Response" : "Profile added", "ID" : newProfile.id}
    
    elif request.method == "GET":
        try:
            userId = request.json["userId"]
        except:
            abort(400)

        if type(userId) != int:
            return {"Status" : "Failure", "Response" : "Invalid user ID"}
        user = User.query.filter_by(id = userId)
        if not user:
            return {"Status" : "Failure", "Response" : "User does not exist"}
        
        profile = Profile.query.filter_by(userId = userId)
        response = {"userId" : user.id, "username" : user.username, "country" : profile.country, "languages" : profile.languages, "birthDate" : profile.birthDate, "about" : profile.about}

        return {"Status" : "Success", "Response" : response}
    else:
        abort(403)

if __name__ == "__main__":
    app.run(debug = True)