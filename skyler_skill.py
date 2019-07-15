import logging
import os
import requests
import json
import time
from collections import OrderedDict
from flask import request as f_request

from flask import Flask
from flask_ask import Ask, request, session, question, statement

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

#modify address of NodeMCU
address = 'http://192.168.22.11'

#sixty seven 앱 실행 웰컴 인텐스
@ask.launch
def launch():
    welcome_text = 'Welcome to a Led Light Management System.'
    return question(welcome_text).reprompt(welcome_text).simple_card('skyler', welcome_text)


@ask.intent('HelloIntent')
def led_on_controller():
    result = 'Hi. My name is Skyler. Nice to meet you.'
    return statement(result).simple_card('skyler', result)

#결석자 확인
@ask.intent('AbsentIntent')
def tell_absent():
    result = ''
    with open('C:/Users/user/Desktop/name.json') as json_file:
        json_data = json.load(json_file)
        json_name = json_data['name']
        for k in json_name.keys():
            json_check = json_name[k]
            if int(json_check['check']) == 0:
                result = result + k
                result = result + " "
    result = result + 'are absent.'
    return statement(result).simple_card('skyler', result)

#누가 왔는지 체크
@ask.intent('CheckIntent', mapping={'name': 'name'})
def check_name(name):
    check_num = 0
    num = 0
    result = name
    with open('C:/Users/user/Desktop/name.json') as json_file:
        json_data = json.load(json_file)
        json_name = json_data['name']
        for k in json_name.keys():
            if k.upper() == result.upper():
                json_check = json_name[k]
                check_num = int(json_check['check'])
                break
            else:
                num = num + 1
        if check_num == 1:
            result = result + ' is here.'	
        else:
            result = result + ' is not here.'
        if num == 5:
            result = name + ' is not found.'
    json_file.close()
    return statement(result).simple_card('skyler', result)

@ask.intent('QuestionIntent')
def question_requestt():
    result = 'This is Raspberry Pi. Bye Bye.'
    return statement(result).simple_card('skyler', result)

@ask.intent('LedOnIntent')
def led_on_controller():
    # results는 알렉사로 보내는 응답 메세지
    result = 'The l.e.d. light was turned on.'
    # 아두이노 호출 하는 부분 response는 안씀
    response = requests.get(address + '/gpio/1');
    print(response.text)
    return statement(result).simple_card('skyler', result)


@ask.intent('LedOffIntent')
def led_off_controller():
    result = 'The l.e.d. light was turned off.'
    # 아두이노 호출하는 부분
    response = requests.get(address + '/gpio/0');

    print(response.text)
    return statement(result).simple_card('skyler', result)


@ask.intent('TemperatureIntent')
def temperature_controller():
    result = 'The degree of temperature is now '
    response = requests.get(address + '/gpio/2');
    # response.text 에 온도 값 들어감
    print(response.text)
    print(type(response.text))

    # result에 온도 정보를 덧 붙임
    # The degree of temperature is now 30 같은 형태로 알렉사로 응답 됨
    result = result + str(response.text)
    return statement(result).simple_card('skyler', result)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hi to me!'
    return question(speech_text).reprompt(speech_text).simple_card('skyler', speech_text)

@app.route("/hello")
def hello_world():
    return 'hello world!!!'

@app.route("/rfid", methods = ['POST', 'GET'])
def check_rfid():
    SerialNum = f_request.args.get('cardId')
    name = ''
    num = 0
    json_write = ''
    with open('C:/Users/user/Desktop/name.json') as json_file:
        json_data = json.load(json_file)
        json_name = json_data['name']
        json_card = json_data['card']
        for k in json_card.keys():
            print(SerialNum)
            if k.upper() == SerialNum.upper():
                name = json_card[k]
                break
            else:
                num = num + 1
        
        for k in json_name.keys():
            if k.upper() == name.upper():
                json_content = json_name[k]
                json_content['check'] = "1"
                json_content['time'] = time.strftime('%c', time.localtime(time.time()))
        json_write = json_data
    json_file.close()
    with open('C:/Users/user/Desktop/name.json', 'w', encoding = 'utf-8') as json_file:
        json.dump(json_write, json_file, ensure_ascii=False, indent="\t")
    json_file.close() 
    return 'Hello'

@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)