from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_mqtt import Mqtt
import requests
import eventlet


eventlet.monkey_patch()

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

@socketio.on('my_broadcast_event', namespace='/test')
def send_content(sent_data):
    #content = sent_data['data']
    #content2 = sent_data['data2']
    response_news = requests.get(url_news)
    data = response_news.json()
    emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': data['genre']}, broadcast=True)

@app.route('/')
def hello():
    return render_template('hello.html')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('device/sensor')
    mqtt.publish('device/sensor', 'hello world!')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    #mqtt.publish('device/sensor', 'message income')
    mqtt.publish('log', 'message income!')
    #data = dict(
    #    topic=message.topic,
    #    payload=message.payload.decode()
    #)
    #response_news = requests.get(url_news)
    #data = response_news.json()
    #emit('my_content', {'title': data['title'], 'url': data['url'],'date': data['date'], 'img': data['img'],'genre': 'MQTT test'}, broadcast=True, namespace='/test')
    emit('my_content', {'title': 'MQTT', 'url': 'mqtt','date': 'mqtt', 'img': 'mqtt','genre': 'MQTT test'}, namespace='/test')
    mqtt.publish('log', 'emit!')

if __name__ == '__main__':
    socketio.run(app)
