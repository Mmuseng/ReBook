from datetime import datetime, timedelta
import jwt
import hashlib
from info import mongo_link
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import certifi

app = Flask(__name__)
app.secret_key = "REBOOK"

SECRET_KEY = 'REBOOK'
tlsCAFile = certifi.where()
client = MongoClient(mongo_link, tlsCAFile=certifi.where())
db = client.rebook


@app.route('/')
def home():
    book_list = list(db.book.find({}, {'_id': False}))
    # 로그인 체크
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        login_flag = True
    except:
        login_flag = False
    return render_template('index.html', books=book_list, login=login_flag)


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route("/login", methods=["POST"])
def login():
    # 로그인
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 비밀번호 암호화를 위한 해쉬값을 만들어 줌.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'id': id_receive,
                                'pw': pw_hash})                              # 아이디와 패스워드가 매칭되는지 판단을 해줌. 매칭되는 사람이 있다면! 로그인에 성공 한것. 매칭이 안되면 회원가입을 해야함.

    if result is not None:                                                   # result가 있다면!
        payload = {
            'user': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)       # 로그인 24시간 유지
        }                                                                    # jwt 토큰을 발행. 놀이공원 자유입장권과 같은 것. 어떤 사람이 언제까지 입장이 유효하다를 적시해줌.
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token}).decode('utf-8')
        # 찾지 못하면,
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up')
def sign_up_template():
    return render_template('sign_up.html')


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    # id 받고
    id_receive = request.form['id_give']
    # pw 받고
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode(
        'utf-8')).hexdigest()          # 해쉬 함수를 걸어준다
    email_receive = request.form['email_give']
    doc = {
        "id": id_receive,                                                     # 아이디
        "pw": pw_hash,                                                        # 비밀번호
        "profile_name": id_receive,                                           # 프로필 이름 기본값은 아이디
        "email" : email_receive                                               # 이메일
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route("/sign_up/id_chkid", methods=["POST"])
def sign_up_check():
    # 아이디 중복 확인
    id_receive = request.form['id_give']
    exists = bool(db.users.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/email_chkid', methods=['POST'])
def check_dup_email():
    # 이메일 중복 확인
    email_receive = request.form['email_give']
    exists = bool(db.users.find_one({"email": email_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/bookadd')
def bookadd_template():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('bookadd.html')
    except jwt.ExpiredSignatureError:
        # 로그인 시간 만료
        flash("로그인이 필요한 페이지입니다.")
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        # 로그인 정보 존재x
        flash("로그인이 필요한 페이지입니다.")
        return redirect(url_for("login"))


@app.route("/book", methods=["POST"])
def book_add():
    title_receive = request.form['title_give']
    author_receive = request.form['author_give']
    desc_receive = request.form['desc_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    count = db.book.estimated_document_count({}) # 테이블 개수 가져오기

    doc = {
        'num':count+1,
        'title':title_receive,
        'author':author_receive,
        'desc':desc_receive,
        'file': f'{filename}.{extension}'
    }

    db.book.insert_one(doc)

    return jsonify({'msg' : '등록 완료!'})


@app.route("/reviewadd/<book_num>")
def review_add(book_num):
    book_info = db.book.find_one({"num": int(book_num)}, {'_id': False})
    return render_template('reviewadd.html', book=book_info)

@app.route("/api/review", methods=["POST"])
def api_review_add():
    book_num = int(request.form['book_num'])
    review = request.form['review']
    review_list = list(db.review.find({}, {'_id': False}))
    count = len(review_list)

    doc = {
        'book_num': book_num,
        'num': count,
        'review': review
    }

    db.review.insert_one(doc)

    return jsonify({'msg' : '등록 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)