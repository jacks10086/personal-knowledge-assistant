# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, ".")
from agent import KnowledgeAssistant

a = KnowledgeAssistant()
print("=== test1: calculate ===")
print(a.chat("帮我算一下 123 * 456"))
print()
print("=== test2: time ===")
print(a.chat("现在几点了？"))
print()
print("=== test3: memory ===")
print(a.chat("我刚才算的那个数，加上1000是多少？"))