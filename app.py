from info import mongo_link
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
import certifi
app = Flask(__name__)

tlsCAFile = certifi.where()
client = MongoClient(mongo_link, tlsCAFile=certifi.where())
db = client.rebook


@app.route('/')
def home():
    book_list = list(db.book.find({}, {'_id': False}))

    return render_template('index.html', books=book_list)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5500, debug=True)
