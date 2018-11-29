from flask import request
from flask_restful import Resource
from deckslash import api, db, bcrypt
from deckslash.models import User, Card, UserSchema, CardSchema
from deckslash.forms import RegistrationForm, LoginForm

class TestUser(Resource):
    def get(self):
        user_schema = UserSchema(many=True)
        output = user_schema.dump(User.query.with_entities(User.name, User.username, User.profile_image, User.bio).all()).data 
        return output, 201

class UserQuery(Resource):
    def post(self):
        user_schema = UserSchema()
        output = user_schema.dump(User.query.with_entities(User.name, User.username, User.profile_image, User.bio).filter_by(id=request.get_json()['username']).first()).data 
        return output, 201

class CardQuery(Resource):
    def post(self):
        term = request.get_json()['term']
        card_schema = CardSchema(many=True)
        if term:
            output = card_schema.dump(Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).filter(Card.title.contains(term)).all()).data
            return output, 201
        else:
            output = card_schema.dump(Card.query.with_entities(Card.title, Card.description, Card.date_posted, Card.link, Card.picture).all()).data 
            return output, 201

class Login(Resource):
    def post(self):
        form = LoginForm(data=request.get_json())
        if form.validate():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                return {'username': user.username}
            else:
                return {'error':'failure'}
        else:
                return {'error':'failure'}

class Register(Resource):
    def post(self):
        form = RegistrationForm(data=request.get_json())
        if form.validate():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username = form.username.data, name = form.name.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return 201
        else:
            return 404

api.add_resource(TestUser, '/testuser')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(UserQuery, '/user')
api.add_resource(CardQuery, '/card')
