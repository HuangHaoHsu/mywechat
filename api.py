from flask import Flask, request, make_response, render_template_string
import hashlib
import time
import os
import logging
from xml.etree import ElementTree as ET

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    logger.info(f"收到验证请求: signature={signature}, timestamp={timestamp}, nonce={nonce}")
    
    # 按照微信的规则进行签名验证
    token = WECHAT_TOKEN
    temp_list = [token, timestamp, nonce]
    temp_list.sort()
    temp_str = ''.join(temp_list)
    hashcode = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
    
    # 验证签名是否匹配
    if hashcode == signature:
        logger.info("签名验证成功")
        return True, echostr
    
    logger.warning(f"签名验证失败: 计算得到 {hashcode} 但期望 {signature}")
    return False, None

@app.route('/', methods=['GET', 'POST'])
def wechat():
    logger.info(f"收到 {request.method} 请求，参数: {request.args}")
    
    if request.method == 'GET':
        # 检查是否是微信服务器验证
        if 'signature' in request.args:
            is_valid, echostr = check_signature()
            if is_valid:
                logger.info(f"验证成功，返回 echostr: {echostr}")
                return echostr
            else:
                logger.warning("验证失败，返回 403")
                return "Signature verification failed", 403
        else:
            # 普通网页访问，返回欢迎页面
            logger.info("普通网页访问，返回欢迎页面")
            return render_template_string(HTML_TEMPLATE)
    else:  # POST 请求
        try:
            # 记录原始请求数据
            raw_data = request.data
            logger.info(f"收到POST数据: {raw_data}")
            
            # 微信服务器在POST请求时也会发送签名参数
            # 注意：有些微信公众号配置不需要在POST请求时验证签名
            if 'signature' in request.args:
                is_valid, _ = check_signature()
                if not is_valid:
                    logger.warning("POST请求签名验证失败")
                    # 为了调试，我们暂时不返回403，继续处理请求
                    # return "Signature verification failed", 403
            
            # 解析XML数据
            try:
                xml_data = ET.fromstring(raw_data)
                logger.info(f"解析XML成功: {ET.tostring(xml_data, encoding='utf-8').decode('utf-8')}")
                
                # 提取消息类型和内容
                msg_type = xml_data.find('MsgType').text
                logger.info(f"消息类型: {msg_type}")
                
                # 提取发送者和接收者信息
                to_user = xml_data.find('FromUserName').text
                from_user = xml_data.find('ToUserName').text
                logger.info(f"发送者: {to_user}, 接收者: {from_user}")
                
                # 无论收到什么类型的消息，都回复HelloWorld
                response = "<xml>\n<ToUserName><![CDATA[{0}]]></ToUserName>\n<FromUserName><![CDATA[{1}]]></FromUserName>\n<CreateTime>{2}</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[HelloWorld]]></Content>\n</xml>"
                now = int(time.time())
                resp_xml = response.format(to_user, from_user, now)
                
                logger.info(f"回复消息: {resp_xml}")
                
                resp = make_response(resp_xml)
                resp.content_type = 'application/xml'
                return resp
                
            except Exception as xml_error:
                logger.error(f"XML解析错误: {str(xml_error)}")
                return f"XML解析错误: {str(xml_error)}", 400
                
        except Exception as e:
            # 处理任何其他错误
            logger.error(f"处理POST请求时发生错误: {str(e)}", exc_info=True)
            return f"服务器错误: {str(e)}", 500

# 确保 Vercel 可以导入 app
# if __name__ == '__main__':
#     app.run()

# 为 Vercel 添加日志处理路由
@app.route('/logs', methods=['GET'])
def view_logs():
    """显示最近的日志（仅用于调试）"""
    try:
        # 在 Vercel 环境中，我们可以通过内存中变量来保存最近的日志
        if not hasattr(app, 'recent_logs'):
            app.recent_logs = []
        
        # 限制日志记录
        max_logs = 100
        
        # 添加当前请求到日志
        app.recent_logs.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 访问日志页面: {request.remote_addr}")
        if len(app.recent_logs) > max_logs:
            app.recent_logs = app.recent_logs[-max_logs:]
        
        # 生成HTML页面
        logs_html = "<h1>日志记录</h1><pre>"
        for log in app.recent_logs:
            logs_html += log + "\n"
        logs_html += "</pre>"
        
        return logs_html
    except Exception as e:
        return f"获取日志时出错: {str(e)}", 500

# 添加自定义日志处理器，将日志存储到应用变量中
class AppLogHandler(logging.Handler):
    def emit(self, record):
        if not hasattr(app, 'recent_logs'):
            app.recent_logs = []
        
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {record.levelname}: {record.getMessage()}"
        app.recent_logs.append(log_entry)
        
        # 限制日志数量
        max_logs = 100
        if len(app.recent_logs) > max_logs:
            app.recent_logs = app.recent_logs[-max_logs:]

# 添加日志处理器到根日志记录器
app_log_handler = AppLogHandler()
logging.getLogger().addHandler(app_log_handler)
