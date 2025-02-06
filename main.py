import itchat
from itchat.content import *
from DeepWechat import DeepWechat

# 初始化 DeepWechat 对象
deepWechat = DeepWechat()
# 发送启动消息
deepWechat.apply_for_start_msg()

# 定义指定的微信对象
target_wechat_name = {"白炳钊", "filehelper"}

# 处理个人消息
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def personal_text_reply(msg):
    try:
        print("收到消息", msg.text)
        # 检查消息发送者是否为指定对象
        if msg['User']['NickName'] not in target_wechat_name and msg['User']['UserName'] not in target_wechat_name:
            return
        # 构造聊天消息
        chat_msg = "{}:{}".format(msg['User'].get('NickName', msg['User']['UserName']), msg.text)
        # 调用 DeepWechat 类的方法处理消息
        deep_seek_content = deepWechat.apply_for_deepseek(chat_msg)
        # 回复消息
        msg.user.send('%s' % deep_seek_content)
    except Exception as e:
        print(f"处理个人消息时出现异常: {e}")

# 处理群聊消息
@itchat.msg_register(TEXT, isGroupChat=True)
def group_text_reply(msg):
    try:
        if "白炳钊" in msg.text:
            if not msg.isAt and "夸" in msg.text:
                # 处理包含“夸”字的群聊消息
                con_text = "这个消息直接回复，不要把思考过程发出来。{}".format(msg.text)
                deep_seek_content = deepWechat.apply_for_group(con_text)
                msg.user.send('%s' % deep_seek_content)
            elif msg.isAt:
                # 处理 @ 机器人的群聊消息
                context = [{"role": "user", "context": msg.text}]
                deep_seek_content = deepWechat.do_apply_deepseek(context)
                msg.user.send('%s' % deep_seek_content)
    except Exception as e:
        print(f"处理群聊消息时出现异常: {e}")

if __name__ == '__main__':
    # 自动登录微信
    itchat.auto_login(True)
    # 运行 itchat
    itchat.run(True)