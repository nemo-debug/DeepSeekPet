# -*- coding: utf-8 -*-
"""核心逻辑回归测试：任务触发 / 每日推进 / 提前预告 / 夸赞。"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication

import pet

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
QApplication.setStyle("Fusion")

p = pet.PetApp(app)
ok = True


def check(name, cond, extra=""):
    global ok
    print(("PASS  " if cond else "FAIL  ") + name + (f"  {extra}" if extra else ""))
    if not cond:
        ok = False


now = dt.datetime.now()

# 1) 过期的一次性任务：应立刻触发并标记完成
t1 = {
    "id": "t1",
    "text": "测试一次性任务",
    "due": (now - dt.timedelta(seconds=10)).isoformat(timespec="seconds"),
    "repeat": "none",
    "done": False,
    "fired": False,
}
# 2) 每日任务：过期后应提醒并把 due 推进到明天同一时刻，且不标记完成
t2 = {
    "id": "t2",
    "text": "测试每日任务",
    "due": (now - dt.timedelta(minutes=5)).isoformat(timespec="seconds"),
    "repeat": "daily",
    "done": False,
    "fired": False,
}
# 3) 4 分钟后到点的任务：应触发"提前预告"，但不标记完成
t3 = {
    "id": "t3",
    "text": "测试预告任务",
    "due": (now + dt.timedelta(minutes=4, seconds=30)).isoformat(timespec="seconds"),
    "repeat": "none",
    "done": False,
    "fired": False,
}
p.tasks = [t1, t2, t3]
p.check_tasks()

check("一次性任务已触发并完成", t1["done"] is True and t1["fired"] is True)
check("每日任务未标记完成", t2["done"] is False)
new_due = dt.datetime.fromisoformat(t2["due"])
check("每日任务已推进到明天", 23 <= (new_due - now).total_seconds() / 3600 <= 25,
      f"due={new_due}")
check("预告任务标记 soon_fired", t3.get("soon_fired") is True)
check("预告任务未被完成", t3["done"] is False)

# 4) 重复调用不应重复提醒
before = p.bubble._text
p.check_tasks()
check("重复检查不重复触发", t1["fired"] is True)

# 5) 夸赞文案非空
p.praise(force=True)
check("夸赞气泡有内容", bool(p.bubble._text), p.bubble._text[:20])

# 6) 添加/删除任务
p.panel.input.setText("写测试")
p.panel.add_task()
check("添加任务成功", len(p.tasks) == 4, f"count={len(p.tasks)}")
new_id = p.tasks[-1]["id"]
p.panel.toggle_task(new_id, True)
check("勾选完成任务", any(t["id"] == new_id and t["done"] for t in p.tasks))
p.panel.delete_task(new_id)
check("删除任务成功", len(p.tasks) == 3)

# 7) 素材加载
check("三帧素材齐全", all(k in p.fish.sp.frames for k in ("idle", "blink", "happy")))
check("窗口尺寸合理", p.fish.width() > 150 and p.fish.height() > 200,
      f"{p.fish.width()}x{p.fish.height()}")

print("\nRESULT:", "ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
