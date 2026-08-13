# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, ".")
from agent import KnowledgeAssistant

a = KnowledgeAssistant()

print("=== Round 1 ===")
a.chat("3 * 7 = ?")
print()
print("=== Round 2 ===")
a.chat("add 100")
print()
print("=== Round 3 ===")
a.chat("what time?")
print()
print("=== Final history ===")
print(f"Total {len(a.conversation_history)} messages")
for m in a.conversation_history:
    role = m.get("role","?")
    c = str(m.get("content",""))[:50]
    print(f"  [{role}] {c}")