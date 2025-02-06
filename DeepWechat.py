import json
import time
import traceback
import ollama
from Util import process_records


class DeepWechat:
    def __init__(self):
        # 读取提示信息
        with open("promot.json", encoding="utf-8") as r:
            self.promot = json.load(r)

        # 初始化个人对话上下文
        self.msg = [
            {'role': 'user', 'content': self.promot['init_msg']}
        ]

        # 初始化群聊对话上下文
        self.group_context = [
            {"role": 'user', 'content': self.promot['kuakua']}
        ]

        # 指定使用的本地模型
        self.model_name = "deepseek-r1:1.5b"

    def init_start_msg(self):
        """
        只保留最初的上下文，即最早的提问和回答
        """
        self.msg = self.msg[:4]
        print("消息长度:", len(self.msg))

    def apply_for_start_msg(self):
        print("开始初始化...")
        response = self._call_model(self.msg)
        self.msg.append({"role": "assistant", "content": response})
        print("初始化成功，开始学习聊天记录：", response)
        self.init_records()

    def _call_model(self, messages):
        """
        调用本地 Ollama 模型进行对话
        尝试 10 次请求，若失败则等待 5 秒后重试
        """
        for attempt in range(10):
            print(f"第 {attempt + 1} 次尝试")
            try:
                result = ollama.chat(model=self.model_name, messages=messages)
                return result["message"]["content"]
            except Exception as e:
                print(f"ERROR================\n网络出错，请稍后再试: {e}")
                time.sleep(5)
        return None

    def apply_for_start_msg_group(self):
        response = self._call_model(self.group_context)
        self.group_context.append({"role": "assistant", "content": response})
        print("初始化成功", self.group_context)

    def apply_for_group(self, message):
        self.group_context.append({
            "role": "user",
            "content": message
        })
        response = self._call_model(self.group_context)

        # 如果消息中包含“结束本轮对话”，则重置群聊上下文
        if "结束本轮对话" in message:
            self.group_context = self.group_context[:2]
        else:
            self.group_context.append({"role": "assistant", "content": response})
        return response

    def apply_for_deepseek(self, messages):
        self.msg.append({
            "role": "user",
            "content": messages
        })
        print("开始请求:", self.msg)
        response = self._call_model(self.msg)
        print("请求结束:", response)
        self.msg.append({"role": "assistant", "content": response})
        return response

    def init_records(self):
        records_text = process_records()
        # 构造学习聊天记录的消息
        records_msg = f"这是我们的聊天记录，如果你学会了，就说一句我最常说的话。\n{records_text}"
        self.msg.append({"role": "user", "content": records_msg})

        response = self._call_model(self.msg)
        print("学习聊天记录成功:", response)
        self.msg.append({"role": "assistant", "content": response})

        # 发送正式开始的消息
        self.msg.append({"role": "user", "content": self.promot['begin_msg']})
        response = self._call_model(self.msg)
        self.msg.append({"role": "assistant", "content": response})
        print(response)


if __name__ == '__main__':
    deep = DeepWechat()
    deep.apply_for_start_msg()