# 使用最新ChatGPT最新API创建的钉钉机器人，模型回复效果与官网的ChatGPT一致
## 注册openai后送18美元，3个月内使用，API调用，0.2美分1000 token
### 可在群内@机器人聊天，也可与机器人单独聊天

## 使用前提
> 1. 因国内IP被封或OpenAI API被墙，因此自己需要有代理，稍后需要配置  
> 2. 有openai账号，注册事项可以参考[此文章](https://juejin.cn/post/7173447848292253704)   
> 3. 创建好api_key, 进入[OpenAI链接](https://platform.openai.com/),右上角点击，进入页面设置  
![image](https://user-images.githubusercontent.com/38237931/222461544-260ef350-2d05-486d-bf36-d078873b0f7a.png)

## 机器人创建及配置

## 使用方法
1. 执行`pip install openai` `pip install flask`等安装必要包，python版本需要3.7.1及以上才可安装到最新版openai
2. 打开`main.py`文件
3. 将`openai.api_key`填写为自己的api key，将`app_secret`填写为机器人的
4. 将os.environ['HTTP_PROXY']和os.environ['HTTPS_PROXY']设置成代理，注意端口设置
5. 执行`python main.py`运行程序.

## 使用预览
![a5891ac551b8f826ea31230c153ce1c](https://user-images.githubusercontent.com/38237931/222902105-a6add51d-7a03-46e0-8112-c4341d1f63f2.jpg)
