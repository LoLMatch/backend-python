from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Profile(db.Model()):
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, nullable = False)
    country = db.Column(db.String(20))
    languages = db.Column(db.String(200))
    birthDate = db.Column(db.Date)
    about = db.Columnn(db.Text)

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
        if not doesUserExist(userId):
            return {"Status" : "Failure", "Response" : "User does not exist"}
        
        suppProfile = Profile.query.filter_by(userId = userId)
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
        if not doesUserExist(userId):
            return {"Status" : "Failure", "Response" : "User does not exist"}
        
        profile = Profile.query.filter_by(userId = userId)
        response = {"userId" : userId, "username" : getUsernameById(userId), "country" : profile.country, "languages" : profile.languages, "birthDate" : profile.birthDate, "about" : profile.about}

        return {"Status" : "Success", "Response" : response}
    else:
        abort(403)

if __name__ == "__main__":
    app.run(debug = True)

def doesUserExist(userId):
    return True

def getUsernameById(userId):
    return ""