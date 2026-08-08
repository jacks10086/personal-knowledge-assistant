# -*- coding: utf-8 -*-
"""个人知识助手 - 最小Agent骨架

基于第1章学到的 ReAct 循环 + 工具调用，
搭一个能对话、能用工具的最小Agent。
"""
import json
import math
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class ToolRegistry:
    """工具注册表 - Agent的双手"""

    @staticmethod
    def calculate(expression: str) -> dict:
        """数学计算"""
        try:
            allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            allowed.update({"abs": abs, "round": round, "min": min, "max": max})
            result = eval(expression, {"__builtins__": {}}, allowed)
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_current_time() -> dict:
        """获取当前时间"""
        now = datetime.now()
        return {
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "weekday": ["周一","周二","周三","周四","周五","周六","周日"][now.weekday()],
        }

    @staticmethod
    def read_file(filepath: str) -> dict:
        """读取文本文件内容"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return {"filepath": filepath, "content": content[:2000], "length": len(content)}
        except Exception as e:
            return {"error": str(e)}


SYSTEM_PROMPT = """# 角色

你是用户的个人知识助手，帮助用户管理知识、回答问题、执行简单任务。

# 工作流程

## Step 1：理解用户需求
- 分析用户想做什么
- 判断是否需要调用工具

## Step 2：调用工具
- 需要计算时用 calculate
- 需要时间时用 get_current_time
- 需要读文件时用 read_file

## Step 3：输出答案
- 用中文回复
- 如果用了工具，简要说明计算过程

# 规则

- 所有回复使用中文
- 不要编造数据，不确定就调用工具
- 文件路径必须是用户明确提供的"""


def get_tools():
    """返回工具定义（给模型看的说明书）"""
    return [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "数学计算，支持加减乘除、三角函数等",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "数学表达式，如 '2+3*4'"}
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "获取当前日期和时间",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取本地文本文件内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "文件路径"}
                    },
                    "required": ["filepath"]
                }
            }
        }
    ]


class KnowledgeAssistant:
    """个人知识助手 - ReAct循环"""

    def __init__(self, api_key=None, base_url=None, model="deepseek-v4-flash"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.tools = ToolRegistry()
        self.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.max_iterations = 10
        self.max_history = 20  # 保留最近20条消息（约10轮对话），超出则截断

    def chat(self, user_input: str) -> str:
        """对话主循环 - ReAct"""
        self.conversation_history.append({"role": "user", "content": user_input})

        for i in range(self.max_iterations):
            # 滑动窗口：只保留 system 提示 + 最近 max_history 条消息
            if len(self.conversation_history) > self.max_history + 1:
                messages = [self.conversation_history[0]] + self.conversation_history[-(self.max_history):]
            else:
                messages = self.conversation_history

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=get_tools(),
                tool_choice="auto",
                temperature=0.3,
                max_tokens=8192,
            )
            msg = response.choices[0].message

            # 没有工具调用 -> 输出答案，结束
            if not msg.tool_calls:
                self.conversation_history.append({"role": "assistant", "content": msg.content})
                return msg.content

            # 有工具调用 -> 执行工具，结果塞回历史
            self.conversation_history.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    }
                    for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                print(f"  [工具] {name}({args})")

                func = getattr(self.tools, name, None)
                if func:
                    result = func(**args)
                else:
                    result = {"error": f"未知工具: {name}"}

                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

        return "（达到最大轮数，未能完成）"

    def reset(self):
        """清空对话历史"""
        self.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]


if __name__ == "__main__":
    assistant = KnowledgeAssistant()
    print("个人知识助手已启动（输入 quit 退出，reset 清空历史）")
    print("-" * 50)

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() == "quit":
            print("再见！")
            break
        if user_input.lower() == "reset":
            assistant.reset()
            print("（已清空对话历史）")
            continue
        if not user_input:
            continue

        print("\n助手: ", end="")
        answer = assistant.chat(user_input)
        print(answer)