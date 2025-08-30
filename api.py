from flask import Flask, request, make_response, render_template_string
import hashlib
import time
from xml.etree import ElementTree as ET

app = Flask(__name__)

# 你的微信公众号配置
WECHAT_TOKEN = "mywechat2025"  # 替换为你在微信公众平台设置的令牌

# 添加一个简单的HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WeChat Bot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f5f5f5; }
        .container { text-align: center; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #07C160; }
    </style>
</head>
<body>
    <div class="container">
        <h1>WeChat Bot</h1>
        <p>This is a WeChat Official Account webhook that responds "HelloWorld" to all messages.</p>
        <p>Status: <strong>Running</strong></p>
    </div>
</body>
</html>
"""

def check_signature():
    """验证微信服务器请求的有效性"""
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echostr = request.args.get('echostr', '')
    
    # 按照微信的规则进行签名验证
    token = WECHAT_TOKEN
    temp_list = [token, timestamp, nonce]
    temp_list.sort()
    temp_str = ''.join(temp_list)
    hashcode = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
    
    # 验证签名是否匹配
    if hashcode == signature:
        return True, echostr
    return False, None

@app.route('/', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 检查是否是微信服务器验证
        if 'signature' in request.args:
            is_valid, echostr = check_signature()
            if is_valid:
                return echostr
            else:
                return "Signature verification failed", 403
        else:
            # 普通网页访问，返回欢迎页面
            return render_template_string(HTML_TEMPLATE)
    else:
        try:
            # 验证请求签名
            is_valid, _ = check_signature()
            if not is_valid:
                return "Signature verification failed", 403
                
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
        except Exception as e:
            # 处理解析错误，返回一个简单的文本响应
            return f"Error: {str(e)}", 400

# 确保 Vercel 可以导入 app
# if __name__ == '__main__':
#     app.run()
