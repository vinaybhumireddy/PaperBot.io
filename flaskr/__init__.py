import os
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, request, url_for
import requests 
import json

_client_id = "3c49486c11e7447df67dbbc26fb1168d"
_client_secret = "076f599533ee5116190e7246b3c1a913c8e2fd31" 
_domain = "http://localhost:5000"

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
    def hello():
        return 'Hello, World!'

    @app.route('/create_bot', methods=['POST'])
    def create_bot():
        if (request.method=="POST"):
            form = request.form
            name = form['bot_name']
            algorithm = form['bot_algorithm']
            bot = Bot(name,algorithm,Log())
            user = User(form['user_name'],bot)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('/'))
        return redirect(url_for('/'))
    @app.route('/check_price')    
    @app.route('/alpacaAuth')
    def alpacaAuth():
        callback_url = _domain + "/alpacaCallback"
        print(callback_url)
        oauth_url = r"https://app.alpaca.markets/oauth/authorize?response_type=code&client_id=" + _client_id + r"&redirect_uri=" + callback_url + r"&state=RUlMvZWMRU1fZvQKk3jOI1XIuGHoD15e&scope=account:write%20trading%20data"
        
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
        print(access_token)
        return redirect(url_for('purchase'))

    @app.route('/api/purchase', methods=['POST'])
    def purchase():
        global access_token
        if (request.method=="POST"):
            buy_url = 'https://paper-api.alpaca.markets/v2/orders'

            # auth header setup
            authorization_header = {"Authorization":"Bearer {}".format(access_token), "Content-Type":"application/json"}
            authorization_header = json.dumps(authorization_header)
            authorization_header = json.loads(authorization_header) 

            # request
            res = requests.post(buy_url, data=request.data, headers=authorization_header)

            return res.json()

    @app.route('/api/sell', methods=['POST'])
    def sell():
        global access_token
        if (request.method=="POST"):
            sell_url = 'https://paper-api.alpaca.markets/v2/orders'

            authorization_header = {"Authorization":"Bearer {}".format(access_token), "Content-Type":"application/json"}
            authorization_header = json.dumps(authorization_header)
            authorization_header = json.loads(authorization_header) 

            # request
            res = requests.post(sell_url, data=request.data, headers=authorization_header)

            return res.json()


