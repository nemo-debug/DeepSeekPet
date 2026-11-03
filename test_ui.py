# -*- coding: utf-8 -*-
"""临时 UI 冒烟测试：起宠物 + 气泡 + 任务面板，截图后退出。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import ImageGrab
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import pet

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
QApplication.setStyle("Fusion")

p = pet.PetApp(app)
p.fish.show()
p.fish.move(1150, 520)

# 造几条演示任务
now = __import__("datetime").datetime.now()
p.tasks = [
    {"id": "a1", "text": "提交数据库实验报告", "due": (now.replace(second=0) + __import__("datetime").timedelta(minutes=42)).isoformat(timespec="seconds"),
     "repeat": "none", "done": False, "fired": False},
    {"id": "a2", "text": "背 50 个单词", "due": (now.replace(second=0) + __import__("datetime").timedelta(hours=3)).isoformat(timespec="seconds"),
     "repeat": "daily", "done": False, "fired": False},
    {"id": "a3", "text": "去操场跑两圈", "due": (now.replace(second=0) - __import__("datetime").timedelta(hours=1)).isoformat(timespec="seconds"),
     "repeat": "none", "done": True, "fired": True},
]
p.panel.refresh()
p.say("叮～「提交数据库实验报告」的时间到啦！", 60000)
p.panel.show_near_fish()


def grab():
    ImageGrab.grab().save(str(Path(__file__).parent / "shot_ui.png"))
    print("shot saved")
    app.quit()


QTimer.singleShot(2200, grab)
sys.exit(app.exec())
