import jwt
import datetime
import hashlib
from info import mongo_link
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)
from datetime import datetime, timedelta

SECRET_KEY = 'REBOOK'

client = MongoClient(mongo_link)
db = client.rebook


@app.route('/')
def home():
    return render_template('index.html')

# 로그인 시간이 만료되면 홈으로 이동.
@app.route('/')
def login_over():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('home.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route("/login", methods=["POST"])
def login():
    # 로그인
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()         # 비밀번호 암호화를 위한 해쉬값을 만들어 줌.
    result = db.users.find_one({'id': id_receive,
                                'pw': pw_hash})                              # 아이디와 패스워드가 매칭되는지 판단을 해줌. 매칭되는 사람이 있다면! 로그인에 성공 한것. 매칭이 안되면 회원가입을 해야함.

    if result is not None:                                                   # result가 있다면!
        payload = {
            'user': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)       # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY,algorithm='HS256')            # jwt 토큰을 발행. 놀이공원 자유입장권과 같은 것. 어떤 사람이 언제까지 입장이 유효하다를 적시해줌.
        return jsonify({'result': 'success', 'token': token})
        # 찾지 못하면,
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up')
def sign_up_template():
    return render_template('sign_up.html')


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    id_receive = request.form['id_give']                                      # id 받고
    pw_receive = request.form['pw_give']                                      # pw 받고
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()          # 해쉬 함수를 걸어준다
    doc = {
        "id": id_receive,                                                     # 아이디
        "pw": pw_hash,                                                        # 비밀번호
        "profile_name": id_receive                                            # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route("/sign_up/chkid", methods=["POST"])
def sign_up_check():
    # 아이디 중복 확인
    id_receive = request.form['id_give']
    exists = bool(db.users.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)