import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO, emit
import requests


class StockData:
    url = {
        'heisei_old': 'https://script.google.com/macros/s/AKfycbyRJa4dBEUJjbz9wf5fkUS1vH7yzXtuOvLfH9g0mSm03DZhYBU/exec',
        'heisei_new': 'https://script.google.com/macros/s/AKfycbxc-TKyZ8Lp-9Ed05et_wIGw55RLGBGwhNSY2lb2z9iQdy1wLs/exec',
        'twitter_old': 'https://script.google.com/macros/s/AKfycbwxttO7TuSOH45BnlHraDtam91MlBdLrREwl_nHFxwpOACC300/exec',
        'twitter_new': 'https://script.google.com/macros/s/AKfycbyhR8HyQKcf2b9wRUmsCm-6D_EK1zFlJzIpPIhrBuRd49FVFtpT/exec',
        'reiwa': 'https://script.google.com/macros/s/AKfycbzBg6CQ_1MCkuFGd3IMzvXw4vDL0v8I5F6VxWq1nYgp63ew44JA/exec',
    }
    data = {}

    def __init__(self):
        if len(StockData.data) == 0:
            StockData.data = dict(zip(self.url.keys(), [None]*len(self.url)))
        return

    @classmethod
    def store(cls):
        for key, data in cls.data.items():
            if data is None:
                cls.data[key] = requests.get(cls.url[key]).json()
        return

    @classmethod
    def pop(cls, key):
        cls.store()
        data, cls.data[key] = cls.data[key], None
        return data


def create_app():
    app = Flask(__name__)
    return app

def create_socketio(app):
    socketio = SocketIO(app)
    return socketio

def create_mqtt(app):
    app.config['MQTT_BROKER_URL'] = 'm16.cloudmqtt.com'
    app.config['MQTT_BROKER_PORT'] = 10145
    app.config['MQTT_USERNAME'] = 'bqntusbe'
    app.config['MQTT_PASSWORD'] = 'FSeMpNi8kNhF'
    app.config['MQTT_KEEPALIVE'] = 5
    app.config['MQTT_TLS_ENABLED'] = False
    mqtt = Mqtt(app)
    return mqtt


app = create_app()
socketio = create_socketio(app)
mqtt = create_mqtt(app)

stock_data = StockData()


@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/helloios')
def helloios():
    return render_template('hello_ios.html')

@app.route('/aboutios')
def aboutios():
    return render_template('about_ios.html')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print('handle_connect_now')
    mqtt.subscribe('device/sensor')
    mqtt.publish('device/sensor', 'handle_connect!')
    return

@socketio.on('my_broadcast_event', namespace='/test')
def send_content(sent_data):
    content2key = {
        'news': 'heisei_new',
        'twitter': 'twitter_new',
        'reiwa': 'reiwa',
    }
    content = sent_data['event']

    data = stock_data.pop(content2key[content])
    emit('my_content', data, broadcast=True)
    stock_data.store()
    return

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    content2key = {
        '+1': 'heisei_old',
        '+2': 'heisei_new',
        '-1': 'twitter_old',
        '-2': 'twitter_new',
        'turn': 'reiwa',
    }
    content = message.payload.decode()
    mqtt.publish('log', f'handle_mqtt_message: {content}')

    data = stock_data.pop(content2key[content])
    socketio.emit('my_content', data, namespace='/test')
    stock_data.store()
    return


if __name__ == '__main__':
    socketio.run(app)
