import os
from flask import Flask,redirect,request, url_for
import os
from flask_sqlalchemy import SQLAlchemy
import requests 
import time
_client_id = "3c49486c11e7447df67dbbc26fb1168d"
_client_secret = "076f599533ee5116190e7246b3c1a913c8e2fd31" 
_domain = "http://localhost:5000"
_bots = dict()
access_token = ""
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    db=SQLAlchemy(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def index():
        return 'Hello, World!'

    @app.route('/create_bot', methods=["POST"])
    @app.route('/update_bot', methods=["POST"])
    def create_bot():
        if (request.method=="POST"):
            form = request.values
            name = form['bot_name']
            algorithm = form['bot_algorithm']
            _bots[name]=algorithm.split()
            print(_bots)
        return redirect(url_for('index')) 

    @app.route('/delete_bot', methods=["POST"])
    def delete_bot():
        if (request.method=="POST"):
            form = request.values
            name = form['bot_name']
            if name in _bots:
                _bots.pop(name,None)
            print(_bots)
        return redirect(url_for('index')) 

    @app.route('process_algorithm')
    def process_algorithm():
        for bot_name in _bot.keys():
            instruction_words_length = len(_bots[name])
            truth_value=True
            i=0
            while (i<instruction_words_length):
                word=_bots[name][i]
                i+=1
                if (word=="if"):
                    condition=_bots[name][i]
                    i+=1
                    value=_bots[name][i]
                    i+=1
                    truth_value = truth_value and process_condition(condition,value)
                if (word=="then"):
                    action=_bots[name][i]
                    i+=1
                    num_shares=_bots[name][i]
                    i+=1
                    stock_name=_bots[name][i]
                    i+=1
                    if (truth_value):
                        execute_order(action,num_shares,stock_name)
            

    @app.route('/alpacaAuth')
    def alpacaAuth():
        callback_url = _domain + "/alpacaCallback"
        print(callback_url)
        oauth_url = "https://app.alpaca.markets/oauth/authorize?response_type=code&client_id=" + _client_id + "&redirect_uri=" + callback_url + "&state=RUlMvZWMRU1fZvQKk3jOI1XIuGHoD15e&scope=account:write%20trading%20data"
        
        return redirect(oauth_url, 302)

    @app.route('/alpacaCallback', methods=['GET','POST'])
    def alpacaCallback():
        global access_token
        callback_url = _domain + "/alpacaCallback"
        code = request.args.get('code')
        
        tokenUrl = 'https://api.alpaca.markets/oauth/token'
        
        data = {'grant_type':'authorization_code',
                'code':code,
                'client_id':_client_id, # client key
                'client_secret':_client_secret, # client secret
                'redirect_uri': callback_url
        }
        
        # TODO: Set a cookie here to allow the user to stay logged in
        res = requests.post(tokenUrl,data=data)
        tempData = res.json()
        access_token=tempData['access_token']
        
        print(tempData)
        return redirect(url_for('purchase'))
        
    @app.route('/purchase')
    def purchase():
        global access_token
        authorization_header = {'Authorization':'Bearer {}'.format(access_token),"Content-Type":"application/json"}
        print(authorization_header)
        print(access_token)
        buy_url = 'https://paper-api.alpaca.markets/v2/orders'
        params_json = {
            "side": "buy",
            "symbol": "IIPR",
            "type": "market",
            "qty": "100",
            "time_in_force": "gtc"
        }
        
        res = requests.post(buy_url, params=params_json, headers=authorization_header)


        return res.json()

    '''''
    This route serves as an interface between the frontend and Alpaca api
    Purchases a specified quantity of shares for specified stock
    '''''
    @app.route('/api/buy')
    def buy():
        return "bought"

    return app

