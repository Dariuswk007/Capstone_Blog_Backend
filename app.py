from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

db = SQLAlchemy(app)
CORS = CORS(app)
ma = Marshmallow(app)

class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String(144), nullable=False)
    image = db.Column(db.Integer, nullable=False)

    def __init__(self, title, description, image):
        self.title = title
        self.description = description
        self.image = image

class AnimeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'image')

anime_schema = AnimeSchema()
multiple_anime_schema = AnimeSchema(many=True)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable = True)
    password = db.Column(db.String(12), nullable = True)
    blogs = db.relationship("Blog", backref = "user", cascade = "all, delete, delete-orphan")

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

class Blog(db.Model):
    __tablename__ = "blog"
    id = db.Column(db.Integer, primary_key=True)
    characters = db.Column(db.String(144), nullable = False)
    user_fk = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, characters, user_fk):
        self.characters = characters
        self.user_fk = user_fk


class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(144), nullable=False)
    review_fk = db.Column(db.Integer, db.ForeignKey('blog.id'))

    def __init__(self, post, review_fk):
        self.post = post
        self.review_fk = review_fk

class ReviewSchema(ma.Schema):
    class Meta:
        fields = ('id', 'post', 'review_fk')

review_schema = ReviewSchema()
multiple_review_schema = ReviewSchema(many=True)

class BlogSchema(ma.Schema):
    class Meta:
        fields = ('id', 'characters', 'user_fk', 'reviews')
    reviews = ma.Nested(multiple_review_schema)

blog_schema = BlogSchema()
multiple_blog_schema = BlogSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_name', 'password', 'blogs')
    blogs = ma.Nested(multiple_blog_schema)


user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)


@app.route('/anime/add', methods=['POST'])
def add_anime():
    post_data = request.get_json()
    title = post_data.get('title')
    description = post_data.get('description')
    image = post_data.get('image')

    new_anime = Anime(title, description, image)
    db.session.add(new_anime)
    db.session.commit()

    return jsonify("a new anime entry has been added.")

@app.route('/user/add', methods=['POST'])
def add_user():
    post_data = request.get_json()
    user_name = post_data.get('user_name')
    password = post_data.get('password')

    new_user = User(user_name, password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify("a new user entry has been added.")


@app.route('/anime/get', methods=['GET'])
def get_anime():
    anime_entries = db.session.query(Anime).all()
    return jsonify(multiple_anime_schema.dump(anime_entries))


@app.route('/user/login', methods=['POST'])
def verify_login():
    if request.content_type != 'application/json':
        return jsonify('Error: Data Data must be JSON.')
    
    post_data = request.get_json()
    user_name = post_data.get('user_name')
    password = post_data.get('password')

    user = db.session.query(User).filter(User.user_name == user_name).first()

    if user is None:
        return jsonify('No user created.')

    return jsonify('User logged in.')

@app.route('/user/get', methods=['GET'])
def get_users():
    users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(users))


@app.route('/blog/add', methods=['POST'])
def add_blog():

    post_data = request.get_json()
    characters = post_data.get('characters')
    user_fk = post_data.get('user_fk')

    new_blog = Blog(characters, user_fk)

    db.session.add(new_blog)
    db.session.commit()

    return jsonify("a new blog has been posted.")

@app.route('/review/add', methods=['POST'])
def add_review():

    post_data = request.get_json()
    post = post_data.get('post')
    review_fk = post_data.get('review_fk')

    new_review = Review(post, review_fk)

    db.session.add(new_review)
    db.session.commit()

    return jsonify("a new review has been posted.")




if __name__ == "__main__":
        app.run(debug=True)