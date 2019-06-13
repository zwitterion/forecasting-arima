'''
sample application
'''

from flask import Flask
import json

app = Flask(__name__)


@app.route('/')
def index():
    '''
    example
    '''
    return "Hello World!"

@app.route('/api/v1.0/query', methods=['GET'])
def do_query():
    '''
    example
    '''
    data = [ {'id':1}, {'id':2}]

    return json.dumps({'q': data})


if __name__ == '__main__':
    app.run(debug=True)