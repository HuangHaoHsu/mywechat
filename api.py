from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # WeChat server validation (Echo back the 'echostr' parameter)
        echostr = request.args.get('echostr', '')
        return make_response(echostr)
    else:
        # Always reply with HelloWorld
        response = "<xml>\n<ToUserName><![CDATA[{0}]]></ToUserName>\n<FromUserName><![CDATA[{1}]]></FromUserName>\n<CreateTime>{2}</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[HelloWorld]]></Content>\n</xml>"
        import time
        from xml.etree import ElementTree as ET
        xml_data = ET.fromstring(request.data)
        to_user = xml_data.find('FromUserName').text
        from_user = xml_data.find('ToUserName').text
        now = int(time.time())
        resp_xml = response.format(to_user, from_user, now)
        resp = make_response(resp_xml)
        resp.content_type = 'application/xml'
        return resp

if __name__ == '__main__':
    app.run()
