
# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import random
from flask import Flask, request
from json_extract import GetValue2

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
moves = ['F','L', 'R', 'F', 'F', 'L', 'R']

@app.route("/", methods=['GET'])
def index():
    return "Let the battle begin!"

@app.route("/", methods=['POST'])
def move():
    data = request.get_json()
    logger.info(request.json)
    t_range, d_range, hit = myself(data)
    response = check(moves, data,t_range, d_range, hit)
    logger.info(response)
    return response


def myself(data):
    records = GetValue2(data)
    me = records.get_values('https://cloud-run-hackathon-python-1-2mlstgvneq-uc.a.run.app')
    x= me['x']
    y= me['y']
    hit=me['wasHit']
    if me['direction'] == 'N':
        target_range= {'x': [x], 'y': (max(0, y-3), max(0, y-2), max(0, y-1))}
        defend_range = {'direction': 'N', 'x': [x], 'y': [max(0, y+2), max(0, y+1)]}
        if y == 0:
            hit=True
    elif me['direction'] == 'E':
        target_range= {'x': [max(0,x+3), max(0,x+2), max(0,x+1)], 'y':[y]}
        defend_range = {'direction': 'E', 'x': [max(0,x-2), max(0,x-1)], 'y':[y]}
    elif me['direction'] == 'S':
        target_range= {'x': [x], 'y': (max(0, y+3), max(0, y+2), max(0, y+1))}
        defend_range = {'direction': 'S', 'x': [x], 'y': [max(0,y-2), max(0,y-1)]}
    elif me['direction'] == 'W':
        target_range= {'x': [max(0,x-3), max(0,x-2), max(0,x-1)], 'y':[y]}
        defend_range = {'direction': 'W', 'x': [max(0,x+2), max(0,x+1)], 'y':[y]}
        if x == 0:
            hit=True
    else:
        raise ValueError('no data found for your url')
    return target_range, defend_range, hit

# loop to check participants
def check(moves, data,target_range, defend_range, hit) :
    for val in data['arena']['state'].values():
        if val['x'] in target_range['x'] and val['y'] in target_range['y']:
            if hit == True:
                response = 'L'
                break
            else:
                response = 'T'
                break
        if val['direction'] == defend_range['direction'] and val['y'] in defend_range['y'] and val['x'] in defend_range['x'] :
            response = 'L'
            break
        else:
            response = moves[random.randrange(len(moves))]
    return response


if __name__ == "__main__":
  app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
  
