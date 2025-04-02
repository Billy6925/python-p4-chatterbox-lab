from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages',methods=['GET','POST'])
def messages():
    if request.method=='GET':
        messages= [message.to_dict() for message in Message.query.order_by('created_at').all()]
        response = make_response(jsonify(messages),200)
        return response
    elif request.method=='POST':
        #Extract form data from request
        data= request.get_json()

        #validate form data
        if not data or "body" not in data or "username" not in data:
            return make_response({'error':'Must include body and username'},400)
        #Create a new message instance
        new_message= Message(body=data['body'],username= data['username'])
        db.session.add(new_message)
        db.session.commit()

        response= make_response(jsonify(new_message.to_dict()),201)
        return response

@app.route('/messages/<int:id>',methods=['GET','PATCH','DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id==id).first()
    if request.method=='GET':
        return make_response(jsonify(message.to_dict()),200)
    elif request.method== 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response({'message':'Message deleted successfully'})
    elif request.method=='PATCH':
        data= request.get_json()
        for key,value in data.items():
            if hasattr(message,key):
                setattr(message,key,value)
        db.session.commit()
        response= make_response(jsonify(message.to_dict()),200)
        return response

if __name__ == '__main__':
    app.run(port=5555)
