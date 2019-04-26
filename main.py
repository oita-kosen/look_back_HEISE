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

url_news = 'https://script.google.com/macros/s/AKfycbykUsL_lHUS2P6i04ONhzS5O0_qonjCPui1SSFFdwe6X-2QEbA/exec'
url_twitter = 'https://script.google.com/macros/s/AKfycbzOmzIjzfwHqVpaUbgNcbm8tVjC9D1p_YwO8_4s/exec'
response_news = requests.get(url_news)
response_twitter = requests.get(url_twitter)


@socketio.on('my_broadcast_event', namespace='/test')
def send_content(sent_data):
    global response_news
    global response_twitter
    content = sent_data['event']
    print(content)

    if content == 'news':
        data = response_news.json()
        emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']}, broadcast=True)
        response_news = requests.get(url_news)

    elif content == 'twitter':
        data = response_twitter.json()
        emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']}, broadcast=True)
        response_twitter = requests.get(url_twitter)


@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/about')
def about():
    return render_template('about.html')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('device/sensor')
    mqtt.publish('device/sensor', 'hello world!')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global response_news
    global response_twitter
    mqtt.publish('log', 'message income!')
    #data = dict(
    #     topic=message.topic,
    #     payload=message.payload.decode()
    #)

    if message.payload.decode() == 'left':  #左向いた時
        data = response_twitter.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt (L)'},
                      namespace='/test')
        response_twitter = requests.get(url_twitter)

    elif message.payload.decode() == 'right':   #右向いたとき
        data = response_news.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt (R)'},
                      namespace='/test')
        response_news = requests.get(url_news)

    else:#それ以外
        data = response_news.json()
        socketio.emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']+' by mqtt ({})'.format(message.payload.decode())},
                      namespace='/test')
        response_news = requests.get(url_news)

    mqtt.publish('log', 'emit!')

if __name__ == '__main__':
    socketio.run(app)
