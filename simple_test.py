from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        return "Hello, this is a simple test server. Send a POST request to test."
    else:
        # 打印所有请求信息
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Args: {dict(request.args)}")
        print(f"Form: {dict(request.form)}")
        print(f"Data: {request.data}")
        
        # 回复简单的消息
        return "Received your POST request!"

if __name__ == '__main__':
    app.run(debug=True)
