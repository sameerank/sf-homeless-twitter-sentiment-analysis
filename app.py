import flask
import requests
import os
import json
import pandas as pd
from config import Config

app = flask.Flask(__name__)

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
def processed():
    url = '/'.join([Config.db_url, '_find'])
    payload = "{\n  \"selector\": {\n    \"_id\": {\n      \"$gt\": 0\n    }\n  },\n  \"fields\": [\n    \"_id\",\n    \"created_at\",\n    \"geo\",\n    \"text\"\n  ]\n}"
    headers = {'content-type': "application/json"}
    r = requests.post(url, data=payload, headers=headers)
    rdata = r.json()['docs']
    df = pd.DataFrame(map(lambda rd: {'id': rd['_id'], 'created_at': rd['created_at'], 'text': rd['text']}, rdata))
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
