from flask import request,jsonify, Flask
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)


app.config["JWT_SECRET_KEY"] = "uoghwiuehgqeijfpowjjpowejpotjewjti3"
jwt = JWTManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///peachy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    to_account = db.Column(db.String, unique = False, nullable = False)
    from_account = db.Column(db.String, unique = False, nullable = False)
    ammount = db.Column(db.Float, nullable = False)
    state = db.Column(db.String, unique = False, nullable = True)
    date = db.Column(db.String, unique = False, nullable = True)
    
    def to_json(self):
        return {
            "id":self.id,
            "toAccount":self.to_account, 
            "fromAccount": self.from_account,
            "ammount": self.ammount,
            "state" : self.state,
            "date" : self.date
        }


@app.route("/api/token", methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@jwt_required()
@app.route("/api/transactions", methods = ["GET"])
def get_transactions():
    transactions = Transaction.query.all()
    json_transactions = list(map(lambda x: x.to_json(), transactions))
    return jsonify({"transactions":json_transactions})

@jwt_required()
@app.route("/api/create_transaction",methods =["POST"])
def create_transaction():
    to_account = request.json.get('toAccount')
    from_account = request.json.get('fromAccount')
    ammount = request.json.get('ammount')
    state = request.json.get('state')
    date = request.json.get('date')
    
    if not to_account or not from_account or not ammount:
        return (
            jsonify({"message":"Please fill all the fields"}), 400,
        )
    new_transaction = Transaction(to_account = to_account, from_account = from_account, ammount = ammount, state = state, date = date)
    try:
        db.session.add(new_transaction)
        db.session.commit()
    except Exception as e :
        return jsonify({"message": str(e)}), 400
    
    return jsonify({"message":"Transaction added"}), 201

@jwt_required()
@app.route("/api/update_state/<int:id>", methods = ["PATCH"])
def update_state(id):
    transaction = Transaction.query.get(id)
    
    if not transaction:
        return jsonify({"message":"Transaction not found"}), 404
    
    data = request.json
    transaction.state = data.get('state', transaction.state)
    db.session.commit()
    return jsonify({'message':'State updated'}), 200
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)