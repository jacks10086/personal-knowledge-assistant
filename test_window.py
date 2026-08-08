# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, ".")
from agent import KnowledgeAssistant

a = KnowledgeAssistant()

# 发4轮对话，测试滑动窗口
for i in range(4):
    q = f"第{i+1}轮：记住我的幸运数字是 {i+1}7"
    print(f"你: {q}")
    r = a.chat(q)
    print(f"助手: {r[:60]}...")
    print(f"  历史长度: {len(a.conversation_history)} 条")
    print()

# 测试第5轮，看它是否还记得第1轮
print("=== 测试记忆 ===")
r = a.chat("我之前告诉你的第一个幸运数字是多少？")
print(f"助手: {r[:100]}")
print(f"  历史长度: {len(a.conversation_history)} 条")