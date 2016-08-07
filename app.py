import flask
import requests
import os
import json
import tweepy
import pandas as pd
from textblob import TextBlob
from dateutil.parser import parse
from config import Config
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

app = flask.Flask(__name__)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/count')
def count():
  url = '/'.join([Config.db_url, '_all_docs']) + '?limit=0'
  r = requests.get(url)
  return flask.jsonify({"count": r.json()['total_rows']})

@app.route('/tweets')
def tweets():
    url = '/'.join([Config.db_url, '_find'])
    payload = "{\n  \"selector\": {\n    \"_id\": {\n      \"$gt\": 0\n    }\n  },\n  \"fields\": [\n    \"_id\",\n    \"created_at\",\n    \"geo\",\n    \"text\"\n  ]\n}"
    headers = {'content-type': "application/json"}
    r = requests.post(url, data=payload, headers=headers)
    return flask.jsonify(r.json())

@app.route('/processed')
@crossdomain(origin='*')
def processed():
    url = '/'.join([Config.db_url, '_find'])
    payload = "{\n  \"selector\": {\n    \"_id\": {\n      \"$gt\": 0\n    }\n  },\n  \"fields\": [\n    \"_id\",\n    \"created_at\",\n    \"geo\",\n    \"text\"\n  ]\n}"
    headers = {'content-type': "application/json"}
    r = requests.post(url, data=payload, headers=headers)
    rdata = r.json()['docs']
    df = pd.DataFrame(map(lambda rd: {'id': rd['_id'], 'created_at': rd['created_at'], 'text': rd['text']}, rdata))
    df['polarity'] = df.apply(lambda x: TextBlob(x['text']).sentiment.polarity, axis=1)
    df['subjectivity'] = df.apply(lambda x: TextBlob(x['text']).sentiment.subjectivity, axis=1)
    df['created_at'] = df.apply(lambda x: parse(x['created_at']), axis=1)
    df.sort_values(by=['created_at'], inplace=True)
    return df.transpose().to_json()

@app.route('/')
def index():
    url = '/'.join([Config.db_url, '_all_docs']) + '?limit=0'
    r = requests.get(url)
    count = r.json()['total_rows']
    return flask.render_template('index.html', count=count)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(port=port)
