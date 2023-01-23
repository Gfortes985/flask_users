import json
import hashlib
import os
import base64
from flask import Flask,make_response,jsonify,request,render_template
from datetime import datetime

app = Flask(__name__)

#код отображения галвной страницы в root'е сайта
@app.route('/',methods=["GET","POST"])
def index():
    return render_template('index.html')

#отлов ошибки 404 и предоставление ее в json формате
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error':'Not found'}),404)

#API для регистрации пользователя возращает ошибку или инфо в json формате
@app.route('/api/register',methods=["GET"])
def register():
    login = request.args.get('login')
    password = request.args.get('password')
    if login == None or password ==  None:
        return make_response(jsonify({'error':'No credentials'}))
    salt = os.urandom(32)
    bsalt = str(base64.b64encode(salt))
    bsalt = bsalt[1:].replace("'", "")
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    bkey = str(base64.b64encode(key))
    bkey = bkey[1:].replace("'", "")
    time = datetime.now().date()
    with open('users.json','r') as users:
        file_js = json.loads(users.read())
    with open('users.json','w') as users:
        file_js[f'{login}'] = {'hash':bkey,"salt":bsalt,"date":f"{time}"}
        users.write(json.dumps(file_js,indent=4))
    return make_response(jsonify({'info': 'user registered'}), 200)

#API для просмотра зарегистрированных пользователей в формате json
@app.route('/api/users')
def users_collection():
    d = {}
    d["users"] = []
    with open('users.json','r') as file:
        file_js = json.loads(file.read())
        for i in file_js:
            d["users"].append(i)
    return d

#API для просмотра данных учетной записи конкретного пользоватля в формате json (http://127.0.0.1:5000/api/users/[username])
@app.route('/api/users/<usr>')
def user_data(usr):
    with open('users.json','r') as file:
        file_js = json.loads(file.read())
        return file_js[f"{usr}"]

#тело запуска сервера в дебаг режиме
if __name__ == '__main__':
    app.run(debug=True)