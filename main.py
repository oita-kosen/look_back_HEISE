import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_mqtt import Mqtt
import requests

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'm16.cloudmqtt.com'
app.config['MQTT_BROKER_PORT'] = 10145
app.config['MQTT_USERNAME'] = 'bqntusbe'
app.config['MQTT_PASSWORD'] = 'FSeMpNi8kNhF'
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
#app.config['MQTT_TLS_INSECURE'] = False
#app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

mqtt = Mqtt(app)

socketio = SocketIO(app)

'''
1が昔の記事とtwitter
2が最近の記事とtwitter
'''

url_news_1 = 'https://script.google.com/macros/s/AKfycbyRJa4dBEUJjbz9wf5fkUS1vH7yzXtuOvLfH9g0mSm03DZhYBU/exec'
url_news_2 = 'https://script.google.com/macros/s/AKfycbxc-TKyZ8Lp-9Ed05et_wIGw55RLGBGwhNSY2lb2z9iQdy1wLs/exec'
url_twitter_1 = 'https://script.google.com/macros/s/AKfycbwxttO7TuSOH45BnlHraDtam91MlBdLrREwl_nHFxwpOACC300/exec'
url_twitter_2 = 'https://script.google.com/macros/s/AKfycbyhR8HyQKcf2b9wRUmsCm-6D_EK1zFlJzIpPIhrBuRd49FVFtpT/exec'
url_turn = 'https://script.google.com/macros/s/AKfycbzBg6CQ_1MCkuFGd3IMzvXw4vDL0v8I5F6VxWq1nYgp63ew44JA/exec'

response_news_1 = None
response_twitter_1 = None
response_news_2 = None
response_twitter_2 = None
response_reiwa = None


@socketio.on('my_broadcast_event', namespace='/test')
def send_content(sent_data):
    global response_news_1
    global response_twitter_1
    global response_news_2
    global response_twitter_2
    global response_reiwa
    content = sent_data['event']
    print(content)

    if response_news_1 is None:
        response_news_1 = requests.get(url_news_1)
    if response_twitter_1 is None:
        response_twitter_1 = requests.get(url_twitter_1)
    if response_news_2 is None:
        response_news_2 = requests.get(url_news_2)
    if response_twitter_2 is None:
        response_twitter_2 = requests.get(url_twitter_2)
    if response_reiwa is None:
        response_reiwa = requests.get(url_turn)

    if content == 'news':
        data = response_news_1.json()
        emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']}, broadcast=True)
        response_news_1 = requests.get(url_news_1)

    elif content == 'twitter':
        data = response_twitter_1.json()
        emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']}, broadcast=True)
        response_twitter_1 = requests.get(url_twitter_1)

    elif content == 'reiwa':
        data = response_reiwa.json()
        emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']}, broadcast=True)
        response_reiwa = requests.get(url_turn)


@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/about')
def about():
    return render_template('about.html')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print('handle_connect_now')
    mqtt.subscribe('device/sensor')
    mqtt.publish('device/sensor', 'hello world!')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global response_news_1
    global response_twitter_1
    global response_news_2
    global response_twitter_2
    global response_reiwa
    mqtt.publish('log', f'message income!: {message.payload.decode()}')
    #data = dict(
    #     topic=message.topic,
    #     payload=message.payload.decode()
    #)
    if response_news_1 is None:
        response_news_1 = requests.get(url_news_1)
    if response_twitter_1 is None:
        response_twitter_1 = requests.get(url_twitter_1)
    if response_news_2 is None:
        response_news_2 = requests.get(url_news_2)
    if response_twitter_2 is None:
        response_twitter_2 = requests.get(url_twitter_2)
    if response_reiwa is None:
        response_reiwa = requests.get(url_turn)

    if message.payload.decode() == '+1':  #右向いた時（遅い時）
        data = response_twitter_1.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt (R_slow)'},
                      namespace='/test')
        response_twitter_1 = requests.get(url_twitter_1)

    elif message.payload.decode() == '+2':   #右向いた時（早い時）
        data = response_twitter_2.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt (R_fast)'},
                      namespace='/test')
        response_twitter_2 = requests.get(url_twitter_2)

    elif message.payload.decode() == '-1':   #左向いた時（遅い時）
        data = response_news_1.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt (L_slow)'},
                      namespace='/test')
        response_news_1 = requests.get(url_news_1)

    elif message.payload.decode() == '-2':   #左向いた時（早い時）
        data = response_news_2.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt (L_fast)'},
                      namespace='/test')
        response_news_2 = requests.get(url_news_2)

    elif message.payload.decode() == 'turn':   #一回転したとき
        data = response_reiwa.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt (L_fast)'},
                      namespace='/test')
        response_reiwa = requests.get(url_news_2)

    else:#それ以外
        data = response_news_1.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt ({})'.format(message.payload.decode())},
                      namespace='/test')
        response_news_1 = requests.get(url_news_1)

    mqtt.publish('log', 'emit!')



if __name__ == '__main__':
    socketio.run(app)
