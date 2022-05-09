from info import mongo_link
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)


client = MongoClient(mongo_link)
db = client.rebook


@app.route('/')
def home():
    return render_template('index.html')
