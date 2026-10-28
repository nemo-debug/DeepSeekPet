# -*- coding: utf-8 -*-
"""大肥鱼桌面宠物 ——  DeepSeek 风格的桌面小伙伴。

功能：
  1. 桌面宠物：透明置顶、可拖拽、会呼吸/眨眼/摆尾/说话
  2. 任务提醒：在面板里输入任务 + 时间，到点鱼会冒泡提醒
  3. 随机夸夸：隔一阵子主动夸你一句
用法：
  双击鱼 → 打开任务面板；右键鱼 → 菜单；拖动鱼 → 换位置
"""

import datetime as dt
import json
import math
import random
import sys
import time
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTime,
    QTimer,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QTextOption,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSystemTrayIcon,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

APP_NAME = "大肥鱼"
APP_SUB = "鲸鱼娘桌宠"
DATA_DIR = Path.home() / ".deepseek_pet"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
else:
    BASE_DIR = Path(__file__).resolve().parent
PET_DIR = BASE_DIR / "assets" / "pet"

TASK_FILE = DATA_DIR / "tasks.json"
CONF_FILE = DATA_DIR / "config.json"

PRAISES = [
    "你不是在熬，你是在攒，攒到某天一次性兑现。",
    "能坚持到现在，你比自己以为的更厉害～",
    "偷偷说一句：我觉得你超可靠。",
    "你认真的样子真的很好看。",
    "刚才那件事你处理得很漂亮呀！",
    "这道坎你都过来了，厉害。",
    "别忘了，你一直在变成更好的自己。",
    "有你这样的主人，我运气真好。",
    "你已经做完很多了，允许自己歇一会儿。",
    "今天也辛苦啦，抱一下。",
    "你的耐心真让人佩服。",
    "换成别人早放弃了，你没有。",
    "我相信你的判断。",
    "你在进步，虽然慢一点，但真的在进步。",
    "你笑起来应该很好看吧。",
    "喝口水吧，顺便夸夸你：真不错。",
    "这么难的活你都接了，勇气满分。",
    "你身上的那种韧劲，很珍贵。",
    "今天也在好好生活，这就够了。",
    "你比自己想象中更值得被喜欢。",
    "刚才那个想法挺妙的，记下来吧。",
    "今天又进步了一点呢",
    "别急，你走得慢但没走错。",
    "有人在偷偷羡慕你的自律。",
    "你已经比昨天更熟练了。",
    "累了就靠一会儿，我在。",
    "这件小事你都做得这么认真，服气。",
    "给你比个心，收好。",
    "你不欠任何人一个完美的结果。",
    "跟你搭伙干活挺踏实的。",
    "你的努力，时间都记着账呢。",
    "今天也谢谢你没放弃呀。",
]

IDLE_TALKS = [
    "呼噜噜……（吐了个泡泡）",
    "记得喝口水呀～",
    "我在呢，一直陪着你。",
    "坐久了，伸个懒腰吧！",
    "要不要看看窗外？",
    "我在这里游来游去，不打扰你。",
    "有点饿了……你吃饭了吗？",
    "眨眼三下，眼睛会舒服一点。",
    "慢慢来，反正我等你。",
]

REMIND_TPL = [
    "叮～「{t}」的时间到啦！",
    "该去做「{t}」了哦，我在这儿等你～",
    "时间到！「{t}」，走起！",
    "嘿，别忘了「{t}」呀。",
]

SOON_TPL = [
    "还有 {m} 分钟就要「{t}」啦，准备一下～",
    "提醒一下：「{t}」再过 {m} 分钟就到点了。",
]

DEFAULT_CONFIG = {
    "pos": None,
    "praise_minutes": 12,
    "sound": True,
    "scale": 1.0,
}

STYLE = """
* { font-family: "Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", sans-serif; }
#Panel { background: #FFFFFF; border-radius: 22px; border: 1px solid #E8EDFA; }
#TitleBar { background: transparent; }
#Title { font-size: 17px; font-weight: 700; color: #1B2559; }
#Sub { font-size: 11.5px; color: #9AA4BC; }
QLineEdit { background: #F5F7FF; border: 1.5px solid #E5EBFB; border-radius: 13px;
            padding: 10px 14px; font-size: 13px; color: #1B2559; }
QLineEdit:focus { border: 1.5px solid #4D6BFE; background: #FFFFFF; }
QTimeEdit { background: #F5F7FF; border: 1.5px solid #E5EBFB; border-radius: 13px;
            padding: 8px 10px; font-size: 13px; color: #1B2559; }
QComboBox { background: #F5F7FF; border: 1.5px solid #E5EBFB; border-radius: 13px;
            padding: 8px 10px; font-size: 13px; color: #1B2559; }
QComboBox::drop-down { border: none; width: 16px; }
QComboBox QAbstractItemView { background: #FFFFFF; border: 1px solid #E5EBFB;
            selection-background-color: #EEF2FF; selection-color: #1B2559; outline: none; }
QPushButton#Primary { background: #4D6BFE; color: #FFFFFF; border: none; border-radius: 13px;
            padding: 10px 18px; font-size: 13px; font-weight: 600; }
QPushButton#Primary:hover { background: #3F5CEE; }
QPushButton#Primary:pressed { background: #324BCF; }
QPushButton#Ghost { background: #F1F5FF; color: #4D6BFE; border: none; border-radius: 13px;
            padding: 9px 14px; font-size: 12.5px; font-weight: 600; }
QPushButton#Ghost:hover { background: #E4EBFF; }
QPushButton#Close { background: transparent; color: #B4BDD2; border: none; font-size: 17px; }
QPushButton#Close:hover { color: #FF6B81; }
QPushButton#Del { background: transparent; color: #A8B3CC; border: none; font-size: 16px; }
QPushButton#Del:hover { color: #FF6B81; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { width: 6px; background: transparent; margin: 2px; }
QScrollBar::handle:vertical { background: #D9E0F2; border-radius: 3px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QCheckBox { spacing: 0px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 9px;
            border: 2px solid #CFD8EE; background: #FFFFFF; }
QCheckBox::indicator:hover { border: 2px solid #4D6BFE; }
QCheckBox::indicator:checked { background: #4D6BFE; border: 2px solid #4D6BFE; }
#TaskRow { background: #FAFBFF; border: 1px solid #EFF3FD; border-radius: 14px; }
#TaskRow:hover { background: #F4F7FF; border: 1px solid #DDE6FB; }
#TaskText { font-size: 13.5px; color: #1B2559; font-weight: 600; }
#TaskMeta { font-size: 11.5px; color: #9AA4BC; }
#Empty { font-size: 12.5px; color: #B4BED4; }
"""


# ---------------------------------------------------------------- 数据层
def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as ex:  # 磁盘异常不该让宠物崩掉
        print("保存失败:", ex)


def diag(msg: str) -> None:
    """把启动诊断写进 startup.log，方便排查打包版问题。"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DATA_DIR / "startup.log", "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
    except Exception:
        pass


def humanize(due: dt.datetime) -> str:
    now = dt.datetime.now()
    secs = (due - now).total_seconds()
    if secs <= 0:
        return "已过期"
    mins = int(secs // 60)
    if mins < 1:
        return "马上就到"
    if mins < 60:
        return f"还有 {mins} 分钟"
    if mins < 60 * 24:
        return f"还有 {mins // 60} 小时 {mins % 60} 分"
    days = mins // (60 * 24)
    if days < 7:
        return f"还有 {days} 天"
    return f"{due.month}月{due.day}日"


class SpriteSet:
    """鲸鱼娘三帧素材：idle / blink / happy。"""

    NAMES = ("idle", "blink", "happy")

    def __init__(self, folder: Path, height: int):
        self.raw: dict[str, QPixmap] = {}
        for k in self.NAMES:
            pm = QPixmap(str(folder / f"{k}.png"))
            if pm.isNull():
                raise RuntimeError(f"素材缺失或损坏：{folder / (k + '.png')}")
            self.raw[k] = pm
        base = self.raw["idle"]
        self.h = int(height)
        self.w = int(round(height * base.width() / base.height()))
        # 2 倍缓存，保证高分屏下清晰
        self.frames = {
            k: v.scaled(
                self.w * 2, self.h * 2, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            for k, v in self.raw.items()
        }
        self._hit = self.frames["idle"].toImage()

    def pick(self, blink: float, happy: float, talk: float = 0.0) -> QPixmap:
        if blink < 0.62:
            return self.frames["blink"]
        if happy > 0.45 or talk > 0.25:
            return self.frames["happy"]
        return self.frames["idle"]

    def hit(self, x: int, y: int, w: int, h: int) -> bool:
        """粗略判断点是否落在角色身上（用于忽略透明角落的点击）。"""
        try:
            ix = int(x * self._hit.width() / w)
            iy = int(y * self._hit.height() / h)
            if 0 <= ix < self._hit.width() and 0 <= iy < self._hit.height():
                return self._hit.pixelColor(ix, iy).alpha() > 24
        except Exception:
            pass
        return True


def make_icon(size: int = 128) -> QIcon:
    for name in ("idle", "happy", "blink"):
        f = PET_DIR / f"{name}.png"
        if f.exists():
            pm = QPixmap(str(f))
            if not pm.isNull():
                return QIcon(
                    pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
    return QIcon()


# ---------------------------------------------------------------- 气泡
class Bubble(QWidget):
    """跟着鱼跑的小气泡对话框，淡入淡出，不吃鼠标事件。"""

    PAD = 15
    W_MAX = 300
    GAP = 6

    def __init__(self, owner):
        super().__init__(
            None,
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput,
        )
        self.owner = owner
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self._text = ""
        self._below = False
        self._font = QFont("Microsoft YaHei UI", 10)
        self._font.setStyleStrategy(QFont.PreferAntialias)
        self._opacity = 1.0
        self._anim = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)

    # -- 布局
    def _content_rect(self) -> QSize:
        fm = QFontMetrics(self._font)
        m = 6  # 与 paintEvent 里的外边距一致
        text_w = self.W_MAX - 2 * m - 2 * self.PAD
        r = fm.boundingRect(
            QRect(0, 0, text_w, 2000), int(Qt.TextWordWrap), self._text
        )
        w = min(text_w, max(60, r.width())) + self.PAD * 2 + 2 * m
        h = r.height() + self.PAD * 2 + self.GAP + 2 * m
        return QSize(int(w), int(h))

    def show_text(self, text: str, ms: int = 6000) -> None:
        self._text = text
        try:
            self.resize(self._content_rect())
            self.reposition()
        except Exception:  # 定位异常不能影响说话
            pass
        self._stop_anim()
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self._fade(1.0, 200, QEasingCurve.OutCubic)
        self._timer.start(max(1500, ms))

    def follow(self) -> None:
        if self.isVisible():
            self.reposition()

    def reposition(self) -> None:
        if not self._text:
            return
        g = self.owner.fish.frameGeometry()
        screen = QGuiApplication.screenAt(g.center()) or QGuiApplication.primaryScreen()
        area = screen.availableGeometry()
        x = int(g.center().x() - self.width() / 2)
        y_above = int(g.top() + 4 - self.height())
        if y_above < area.top() + 4:
            self._below = True
            y = int(g.top() + g.height() * 0.62)
        else:
            self._below = False
            y = y_above
        x = max(area.left() + 4, min(x, area.right() - self.width() - 4))
        self.move(x, y)
        self._avoid_panel(x, y, g, area)
        self.update()

    def _avoid_panel(self, x: int, y: int, g, area) -> None:
        """面板打开时别把气泡压在面板底下。"""
        panel = getattr(self.owner, "panel", None)
        if panel is None or not panel.isVisible():
            return
        pr = panel.frameGeometry()
        if not pr.intersects(QRect(x, y, self.width(), self.height())):
            return
        nx = pr.right() + 10
        if nx + self.width() <= area.right() - 4:
            self.move(nx, y)
            return
        self._below = True
        ny = g.top() + int(self.owner.fish.height() * 0.58)
        self.move(x, min(ny, area.bottom() - self.height() - 4))

    def _fade(self, to: float, ms: int, curve=QEasingCurve.InOutQuad) -> None:
        self._stop_anim()
        anim = QPropertyAnimation(self, b"windowOpacity", self)
        anim.setDuration(ms)
        anim.setStartValue(self.windowOpacity())
        anim.setEndValue(to)
        anim.setEasingCurve(curve)
        anim.finished.connect(lambda: self._on_fade_done(anim, to))
        self._anim = anim
        anim.start()

    def _on_fade_done(self, anim, target: float) -> None:
        if self._anim is anim:
            self._anim = None
        if target <= 0.01:
            self._after_hide()

    def _stop_anim(self) -> None:
        anim = self._anim
        self._anim = None
        if anim is not None:
            try:
                anim.stop()
            except RuntimeError:
                pass

    def _fade_out(self) -> None:
        self._fade(0.0, 260)

    def _after_hide(self) -> None:
        self.hide()
        self._text = ""

    def paintEvent(self, ev) -> None:
        if not self._text:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = self.width(), self.height()
        m = 6
        body = QRectF(m, m, w - 2 * m, h - 2 * m - self.GAP)

        # 柔和投影
        for i, a in ((6, 12), (4, 16), (2, 22)):
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(28, 44, 110, a))
            p.drawRoundedRect(body.adjusted(-i, -i + 2, i, i + 2), 16 + i, 16 + i)

        # 尾巴
        cx = w / 2
        tail = QPainterPath()
        if self._below:
            top = body.top()
            tail.moveTo(cx - 9, top + 1)
            tail.lineTo(cx + 9, top + 1)
            tail.lineTo(cx, top - 9)
        else:
            bot = body.bottom()
            tail.moveTo(cx - 9, bot - 1)
            tail.lineTo(cx + 9, bot - 1)
            tail.lineTo(cx, bot + 9)
        tail.closeSubpath()
        p.setBrush(QColor("#FFFFFF"))
        p.drawPath(tail)

        # 气泡主体
        p.drawRoundedRect(body, 16, 16)
        p.setPen(QPen(QColor(226, 233, 250), 1.2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(body, 16, 16)

        # 文字
        p.setPen(QColor("#26314F"))
        p.setFont(self._font)
        tr = body.adjusted(self.PAD, self.PAD, -self.PAD, -self.PAD)
        opt = QTextOption(Qt.AlignmentFlag.AlignLeft)
        opt.setWrapMode(QTextOption.WrapMode.WordWrap)
        p.drawText(tr, self._text, opt)


# ---------------------------------------------------------------- 宠物本体
class FishWindow(QWidget):
    SIZE = 240
    BASE_H = 296

    def __init__(self, owner):
        super().__init__(
            None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.owner = owner
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowTitle(APP_NAME)
        self.sp = SpriteSet(PET_DIR, int(self.BASE_H * owner.scale_factor))
        self.resize(self.sp.w, self.sp.h + 22)
        self.setCursor(Qt.OpenHandCursor)

        self.t = 0.0
        self.blink = 1.0
        self.talk = 0.0
        self.happy = 0.0
        self._talk_target = 0.0
        self._happy_target = 0.0
        self._talk_until = 0.0
        self._happy_until = 0.0
        self._blinking = False
        self._blink_t = 0.0
        self._next_blink = random.uniform(1.2, 3.5)

        self._press_pos = QPoint()
        self._win_pos = QPoint()
        self._moved = False
        self._dragging = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    # -- 动画
    def _tick(self) -> None:
        self.t += 0.033
        now = time.time()

        if self._blinking:
            self._blink_t += 0.033
            ph = self._blink_t / 0.17
            if ph >= 1.0:
                self.blink = 1.0
                self._blinking = False
                self._next_blink = random.uniform(2.0, 6.0)
            else:
                self.blink = abs(math.cos(ph * math.pi))
        else:
            self._next_blink -= 0.033
            if self._next_blink <= 0:
                self._blinking = True
                self._blink_t = 0.0

        self._talk_target = (
            0.45 + 0.55 * abs(math.sin(self.t * 11)) if now < self._talk_until else 0.0
        )
        self._happy_target = 1.0 if now < self._happy_until else 0.0
        self.talk += (self._talk_target - self.talk) * 0.3
        self.happy += (self._happy_target - self.happy) * 0.12
        self.update()

    def talk_for(self, secs: float) -> None:
        self._talk_until = time.time() + secs

    def happy_for(self, secs: float) -> None:
        self._happy_until = time.time() + secs

    def apply_scale(self, scale: float) -> None:
        """换尺寸：重新加载素材并按新比例调整窗口。"""
        self.sp = SpriteSet(PET_DIR, int(self.BASE_H * scale))
        self.resize(self.sp.w, self.sp.h + 22)
        self.update()

    # -- 绘制
    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w, h = self.width(), self.height()
        bob = math.sin(self.t * 1.5) * 2.6 + math.sin(self.t * 3.0) * 0.7
        bob -= self.happy * 3.5
        if self.talk > 0.05:
            bob += abs(math.sin(self.t * 10)) * 1.6
        breathe = 1.0 + 0.010 * math.sin(self.t * 1.5)
        sway = math.sin(self.t * 0.9) * 0.8 + (self.happy * math.sin(self.t * 8) * 1.4)

        # 脚下投影
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(22, 32, 72, 46))
        p.drawEllipse(
            QRectF(w * 0.5 - self.sp.w * 0.26, h - 17, self.sp.w * 0.52, 11)
        )

        pm = self.sp.pick(self.blink, self.happy, self.talk)
        p.save()
        p.translate(w / 2.0, h - 8 + bob)
        p.rotate(sway)
        p.scale(breathe, breathe)
        p.drawPixmap(
            QRectF(-self.sp.w / 2.0, -self.sp.h, self.sp.w, self.sp.h),
            pm,
            QRectF(pm.rect()),
        )
        p.restore()
        p.end()

    # -- 鼠标
    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton:
            pos = ev.position()
            if not self.sp.hit(int(pos.x()), int(pos.y()), self.width(), self.height()):
                ev.ignore()
                return
            self._dragging = True
            self._moved = False
            self._press_pos = ev.globalPosition().toPoint()
            self._win_pos = self.pos()
            self.setCursor(Qt.ClosedHandCursor)
            ev.accept()

    def mouseMoveEvent(self, ev) -> None:
        if not self._dragging:
            return
        delta = ev.globalPosition().toPoint() - self._press_pos
        if delta.manhattanLength() > 3:
            self._moved = True
        self.move(self._win_pos + delta)
        self.owner.bubble.follow()
        ev.accept()

    def mouseReleaseEvent(self, ev) -> None:
        if ev.button() != Qt.LeftButton:
            return
        self._dragging = False
        self.setCursor(Qt.OpenHandCursor)
        if not self._moved:
            self.owner.on_pet_clicked()
        else:
            # 夹回可见范围，避免被拖丢到屏幕外
            self.owner.save_position()
            pos = self.owner.config.get("pos")
            if pos:
                self.move(int(pos[0]), int(pos[1]))
        ev.accept()

    def mouseDoubleClickEvent(self, ev) -> None:
        self._moved = True  # 避免双击后再触发单击台词
        self.owner.open_panel()
        ev.accept()

    def contextMenuEvent(self, ev) -> None:
        pos = ev.pos()
        if not self.sp.hit(pos.x(), pos.y(), self.width(), self.height()):
            ev.ignore()
            return
        self.owner.build_menu().exec(ev.globalPos())
        ev.accept()

    def moveEvent(self, ev) -> None:
        super().moveEvent(ev)
        if getattr(self.owner, "bubble", None) is not None:
            self.owner.bubble.follow()


# ---------------------------------------------------------------- 任务面板
class TitleBar(QWidget):
    def __init__(self, panel: "TaskPanel"):
        super().__init__(panel)
        self.panel = panel
        self.setObjectName("TitleBar")
        self.setFixedHeight(46)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 4, 2, 0)
        lay.setSpacing(8)
        self.title = QLabel("大肥鱼的待办")
        self.title.setObjectName("Title")
        self.sub = QLabel("到点我会来喊你")
        self.sub.setObjectName("Sub")
        col = QVBoxLayout()
        col.setSpacing(1)
        col.setContentsMargins(0, 0, 0, 0)
        col.addWidget(self.title)
        col.addWidget(self.sub)
        lay.addLayout(col)
        lay.addStretch(1)
        close = QPushButton("×")
        close.setObjectName("Close")
        close.setFixedSize(28, 28)
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(panel.hide)
        lay.addWidget(close)
        self._p = QPoint()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton:
            self._p = ev.globalPosition().toPoint() - self.panel.frameGeometry().topLeft()

    def mouseMoveEvent(self, ev) -> None:
        if ev.buttons() & Qt.LeftButton:
            self.panel.move(ev.globalPosition().toPoint() - self._p)


class TaskRow(QFrame):
    def __init__(self, task: dict, panel: "TaskPanel"):
        super().__init__()
        self.task = task
        self.panel = panel
        self.setObjectName("TaskRow")
        self.setFixedHeight(58)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 8, 8)
        lay.setSpacing(10)

        self.cb = QCheckBox()
        self.cb.setCursor(Qt.PointingHandCursor)
        self.cb.setChecked(bool(task.get("done")))
        self.cb.clicked.connect(self._toggle)
        lay.addWidget(self.cb)

        col = QVBoxLayout()
        col.setSpacing(2)
        col.setContentsMargins(0, 0, 0, 0)
        self.lab = QLabel(task["text"])
        self.lab.setObjectName("TaskText")
        self.lab.setWordWrap(False)
        fm = QFontMetrics(self.lab.font())
        self.lab.setText(
            fm.elidedText(task["text"], Qt.ElideRight, 230)
        )
        self.lab.setToolTip(task["text"])
        self.meta = QLabel(self._meta_text())
        self.meta.setObjectName("TaskMeta")
        col.addWidget(self.lab)
        col.addWidget(self.meta)
        lay.addLayout(col, 1)

        delb = QPushButton("×")
        delb.setObjectName("Del")
        delb.setFixedSize(24, 24)
        delb.setCursor(Qt.PointingHandCursor)
        delb.setToolTip("删除")
        delb.clicked.connect(lambda: self.panel.delete_task(self.task["id"]))
        lay.addWidget(delb)

        if task.get("done"):
            self.lab.setStyleSheet("color:#A9B2C7; text-decoration: line-through;")
            self.meta.setStyleSheet("color:#C3CADC;")

    def _meta_text(self) -> str:
        due = dt.datetime.fromisoformat(self.task["due"])
        repeat = " · 每天" if self.task.get("repeat") == "daily" else ""
        if self.task.get("done"):
            return f"{due:%H:%M}{repeat} · 已完成"
        return f"{due:%H:%M}{repeat} · {humanize(due)}"

    def _toggle(self) -> None:
        self.panel.toggle_task(self.task["id"], self.cb.isChecked())


class TaskPanel(QWidget):
    W, H = 452, 566

    def __init__(self, owner):
        super().__init__(
            None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.owner = owner
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setWindowTitle(f"{APP_NAME} · 任务")
        self.setFixedSize(self.W, self.H)
        self.setStyleSheet(STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        panel = QFrame()
        panel.setObjectName("Panel")
        outer.addWidget(panel)
        sh = QGraphicsDropShadowEffect(self)
        sh.setBlurRadius(34)
        sh.setOffset(0, 8)
        sh.setColor(QColor(24, 40, 100, 58))
        panel.setGraphicsEffect(sh)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(18, 10, 18, 16)
        lay.setSpacing(10)
        lay.addWidget(TitleBar(self))

        # 输入框
        self.input = QLineEdit()
        self.input.setPlaceholderText("要提醒我做什么？")
        self.input.returnPressed.connect(self.add_task)
        lay.addWidget(self.input)

        # 时间 + 重复 + 添加
        row = QHBoxLayout()
        row.setSpacing(8)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        nxt = dt.datetime.now() + dt.timedelta(minutes=30)
        self.time_edit.setTime(QTime(nxt.hour, nxt.minute))
        self.time_edit.setFixedWidth(84)
        row.addWidget(self.time_edit)

        self.repeat_box = QComboBox()
        self.repeat_box.addItems(["只提醒一次", "每天提醒"])
        self.repeat_box.setFixedWidth(116)
        row.addWidget(self.repeat_box)

        row.addStretch(1)
        add = QPushButton("添加任务")
        add.setObjectName("Primary")
        add.setCursor(Qt.PointingHandCursor)
        add.clicked.connect(self.add_task)
        row.addWidget(add)
        lay.addLayout(row)

        # 快捷时间
        quick = QHBoxLayout()
        quick.setSpacing(8)
        lbl = QLabel("快捷：")
        lbl.setObjectName("Sub")
        quick.addWidget(lbl)
        for mins in (15, 30, 60):
            b = QPushButton(f"{mins} 分钟后")
            b.setObjectName("Ghost")
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(28)
            b.clicked.connect(lambda _=False, m=mins: self._set_quick(m))
            quick.addWidget(b)
        quick.addStretch(1)
        lay.addLayout(quick)

        # 列表
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_host = QWidget()
        self.list_lay = QVBoxLayout(self.list_host)
        self.list_lay.setContentsMargins(0, 2, 4, 2)
        self.list_lay.setSpacing(8)
        self.list_lay.addStretch(1)
        self.scroll.setWidget(self.list_host)
        lay.addWidget(self.scroll, 1)

        # 底部
        bottom = QHBoxLayout()
        self.count_lab = QLabel("")
        self.count_lab.setObjectName("Sub")
        bottom.addWidget(self.count_lab)
        bottom.addStretch(1)
        praise = QPushButton("夸我一句")
        praise.setObjectName("Ghost")
        praise.setCursor(Qt.PointingHandCursor)
        praise.clicked.connect(lambda: self.owner.praise(force=True))
        bottom.addWidget(praise)
        lay.addLayout(bottom)

        self.refresh()

    # -- 交互
    def _set_quick(self, mins: int) -> None:
        t = dt.datetime.now() + dt.timedelta(minutes=mins)
        self.time_edit.setTime(QTime(t.hour, t.minute))
        self.input.setFocus()

    def add_task(self) -> None:
        text = self.input.text().strip()
        if not text:
            self.owner.say("先写点什么吧，比如「喝水」～", 3500)
            self.input.setFocus()
            return
        t = self.time_edit.time()
        now = dt.datetime.now()
        due = now.replace(hour=t.hour(), minute=t.minute(), second=0, microsecond=0)
        if due <= now:
            due += dt.timedelta(days=1)
        task = {
            "id": f"{int(time.time() * 1000)}{random.randint(10, 99)}",
            "text": text,
            "due": due.isoformat(timespec="seconds"),
            "repeat": "daily" if self.repeat_box.currentIndex() == 1 else "none",
            "done": False,
            "fired": False,
            # 刚建的任务如果本来就在 5 分钟内，就别再"提前预告"一次了
            "soon_fired": (due - now).total_seconds() <= 300,
        }
        self.owner.tasks.append(task)
        self.owner.save_tasks()
        self.input.clear()
        self.refresh()
        self.owner.say(
            f"好，{due.hour:02d}:{due.minute:02d} 我会喊你「{text}」！", 4200
        )
        self.owner.fish.happy_for(2.5)

    def refresh(self) -> None:
        while self.list_lay.count() > 1:
            item = self.list_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        tasks = sorted(
            self.owner.tasks,
            key=lambda x: (x.get("done", False), x["due"]),
        )
        pending = [t for t in self.owner.tasks if not t.get("done")]
        if not tasks:
            empty = QLabel("还没有任务，加一个吧～")
            empty.setObjectName("Empty")
            empty.setAlignment(Qt.AlignCenter)
            empty.setFixedHeight(120)
            self.list_lay.insertWidget(0, empty)
        else:
            for t in tasks:
                self.list_lay.insertWidget(self.list_lay.count() - 1, TaskRow(t, self))
        self.count_lab.setText(
            f"共 {len(pending)} 个待办" if pending else "全部完成，真不错！"
        )

    def toggle_task(self, tid: str, done: bool) -> None:
        for t in self.owner.tasks:
            if t["id"] == tid:
                t["done"] = done
                if done:
                    t["fired"] = True
                elif t.get("repeat") == "daily":
                    t["fired"] = False
                break
        self.owner.save_tasks()
        self.refresh()
        if done:
            self.owner.say(random.choice(PRAISES), 3800)

    def delete_task(self, tid: str) -> None:
        self.owner.tasks = [t for t in self.owner.tasks if t["id"] != tid]
        self.owner.save_tasks()
        self.refresh()

    def show_near_fish(self) -> None:
        fg = self.owner.fish.frameGeometry()
        screen = QGuiApplication.screenAt(fg.center()) or QGuiApplication.primaryScreen()
        area = screen.availableGeometry()
        gap = 18

        # 优先放在鱼的左侧，其次右侧，再次上方，最后下方
        x = fg.left() - self.W - gap
        y = fg.center().y() - self.H // 2
        if x < area.left() + 8:
            x = fg.right() + gap
            if x + self.W > area.right() - 8:
                x = fg.center().x() - self.W // 2
                y = fg.top() - self.H - gap
                if y < area.top() + 8:
                    y = fg.bottom() + gap
        y = max(area.top() + 8, min(y, area.bottom() - self.H - 8))
        x = max(area.left() + 8, min(x, area.right() - self.W - 8))
        self.move(int(x), int(y))
        self.show()
        self.raise_()
        self.activateWindow()
        self.input.setFocus()
        self.refresh()


# ---------------------------------------------------------------- 控制器
class PetApp(QObject):
    def __init__(self, qapp: QApplication):
        super().__init__()
        self.qapp = qapp
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.config = {**DEFAULT_CONFIG, **load_json(CONF_FILE, {})}
        self.tasks: list[dict] = load_json(TASK_FILE, [])
        if not isinstance(self.tasks, list):
            self.tasks = []
        try:
            self.scale_factor = min(1.6, max(0.7, float(self.config.get("scale") or 1.0)))
        except (TypeError, ValueError):
            self.scale_factor = 1.0
        self.last_soon = {}

        self.bubble = Bubble(self)
        self.fish = FishWindow(self)
        self.panel = TaskPanel(self)
        self.panel.hide()

        self._place_fish()
        self.fish.show()
        self.bubble.raise_()
        self._setup_tray()

        self.task_timer = QTimer(self)
        self.task_timer.timeout.connect(self.check_tasks)
        self.task_timer.start(5000)

        self.praise_timer = QTimer(self)
        self.praise_timer.setSingleShot(True)
        self.praise_timer.timeout.connect(self._praise_tick)
        self.schedule_praise()

        QTimer.singleShot(700, self._greet)

        try:
            files = sorted(p.name for p in PET_DIR.glob("*.png")) if PET_DIR.exists() else []
            fw = self.fish
            diag(
                f"frozen={getattr(sys, 'frozen', False)} base={BASE_DIR} "
                f"pet_dir_exists={PET_DIR.exists()} files={files} "
                f"sprite={fw.sp.w}x{fw.sp.h} win={fw.width()}x{fw.height()} "
                f"geom={fw.geometry().getRect()} visible={fw.isVisible()} "
                f"screen={QGuiApplication.primaryScreen().availableGeometry().getRect()}"
            )
        except Exception as ex:
            diag(f"diag error: {ex}")

    # -- 启动
    def _place_fish(self) -> None:
        w, h = self.fish.width(), self.fish.height()
        screen = QGuiApplication.primaryScreen()
        area = screen.availableGeometry()
        pos = self.config.get("pos")
        if pos and isinstance(pos, (list, tuple)) and len(pos) == 2:
            x, y = int(pos[0]), int(pos[1])
            # 严格夹回可见区域（换分辨率/多屏后旧坐标可能越界）
            x = max(area.left() + 4, min(x, area.right() - w - 4))
            y = max(area.top() + 4, min(y, area.bottom() - h - 4))
        else:
            x = area.right() - w - 40
            y = area.bottom() - h - 40
        self.fish.move(x, y)

    def _greet(self) -> None:
        n = len([t for t in self.tasks if not t.get("done")])
        if self.config.get("first_run", True):
            self.config["first_run"] = False
            self.save_config()
            self.say("我来了！双击我可以添加任务哦～", 6000)
        elif n:
            self.say(f"我回来了～今天还有 {n} 件事要提醒你。", 5500)
        else:
            self.say("我回来啦，今天想让我提醒你点什么？", 5000)
        self.fish.happy_for(2.0)

    def _setup_tray(self) -> None:
        self.tray = QSystemTrayIcon(make_icon(64), self)
        self.tray.setToolTip(f"{APP_NAME} · 点我打开任务")
        self.tray.setContextMenu(self.build_menu())
        self.tray.activated.connect(self._tray_clicked)
        self.tray.show()

    def _tray_clicked(self, reason) -> None:
        if reason in (
            QSystemTrayIcon.Trigger,
            QSystemTrayIcon.DoubleClick,
        ):
            self.open_panel()

    # -- 说话
    def say(self, text: str, ms: int = 6000) -> None:
        self.bubble.show_text(text, ms)
        self.fish.talk_for(min(4.0, ms / 1000.0))
        self.bubble.raise_()

    def on_pet_clicked(self) -> None:
        text = random.choice(PRAISES) if random.random() < 0.45 else random.choice(IDLE_TALKS)
        self.say(text, 4200)
        self.fish.happy_for(1.8)

    # -- 夸夸
    def schedule_praise(self) -> None:
        minutes = int(self.config.get("praise_minutes", 12))
        if minutes <= 0:
            self.praise_timer.stop()
            return
        delay = (minutes + random.uniform(-2.5, 3.0)) * 60 * 1000
        self.praise_timer.start(int(max(60, delay)))

    def _praise_tick(self) -> None:
        self.praise(force=False)
        self.schedule_praise()

    def praise(self, force: bool = True) -> None:
        self.say(random.choice(PRAISES), 6000)
        self.fish.happy_for(3.0)

    # -- 任务
    def save_tasks(self) -> None:
        save_json(TASK_FILE, self.tasks)

    def save_config(self) -> None:
        save_json(CONF_FILE, self.config)

    def save_position(self) -> None:
        p = self.fish.pos()
        w, h = self.fish.width(), self.fish.height()
        screen = QGuiApplication.screenAt(self.fish.frameGeometry().center())
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        area = screen.availableGeometry()
        x = max(area.left() + 4, min(p.x(), area.right() - w - 4))
        y = max(area.top() + 4, min(p.y(), area.bottom() - h - 4))
        self.config["pos"] = [x, y]
        self.save_config()

    def check_tasks(self) -> None:
        now = dt.datetime.now()
        changed = False
        for task in list(self.tasks):
            if task.get("done"):
                continue
            try:
                due = dt.datetime.fromisoformat(task["due"])
            except Exception:
                continue
            left = (due - now).total_seconds()
            # 提前 5 分钟预告（每个任务每次只提示一次）
            if 60 < left <= 300 and not task.get("soon_fired"):
                task["soon_fired"] = True
                changed = True
                m = max(1, int(round(left / 60)))
                self.say(random.choice(SOON_TPL).format(t=task["text"], m=m), 5000)
                continue
            if left <= 0 and not task.get("fired"):
                self._fire(task, now)
                changed = True
        if changed:
            self.save_tasks()
            if self.panel.isVisible():
                self.panel.refresh()

    def _fire(self, task: dict, now: dt.datetime) -> None:
        self.say(random.choice(REMIND_TPL).format(t=task["text"]), 9000)
        self.fish.happy_for(4.0)
        if self.config.get("sound", True):
            QApplication.beep()
        if task.get("repeat") == "daily":
            due = dt.datetime.fromisoformat(task["due"])
            while due <= now:
                due += dt.timedelta(days=1)
            task["due"] = due.isoformat(timespec="seconds")
            task["fired"] = False
            task["soon_fired"] = False
        else:
            task["fired"] = True
            task["done"] = True

    # -- 面板 / 菜单
    def open_panel(self) -> None:
        self.panel.show_near_fish()

    def build_menu(self) -> QMenu:
        m = QMenu()
        m.setStyleSheet(
            "QMenu { background:#FFFFFF; border:1px solid #E3E9F8; border-radius:10px; padding:6px; }"
            "QMenu::item { padding:7px 22px 7px 14px; border-radius:7px; font-size:12.5px; color:#1B2559;"
            ' font-family:"Microsoft YaHei UI"; }'
            "QMenu::item:selected { background:#EEF2FF; }"
            "QMenu::separator { height:1px; background:#EEF1F8; margin:4px 8px; }"
        )
        m.addAction("任务清单…   双击我", self.open_panel)
        m.addAction("加个任务…", self.open_panel)
        m.addAction("夸我一句", lambda: self.praise(force=True))
        m.addSeparator()

        sub = m.addMenu("夸夸频率")
        sub.setStyleSheet(m.styleSheet())
        cur = int(self.config.get("praise_minutes", 12))
        for label, mins in (("每 5 分钟", 5), ("每 10 分钟", 10), ("每 15 分钟", 15), ("每 30 分钟", 30), ("关掉夸夸", 0)):
            act = QAction(label, sub)
            act.setCheckable(True)
            act.setChecked(cur == mins)
            act.triggered.connect(lambda _=False, mm=mins: self.set_praise_interval(mm))
            sub.addAction(act)

        snd = QAction("提醒时响一声", m)
        snd.setCheckable(True)
        snd.setChecked(bool(self.config.get("sound", True)))
        snd.triggered.connect(lambda v: self._set_sound(v))
        m.addAction(snd)

        size_menu = m.addMenu("大小")
        size_menu.setStyleSheet(m.styleSheet())
        for label, sc in (("小一点", 0.78), ("中（默认）", 1.0), ("大一点", 1.28)):
            act = QAction(label, size_menu)
            act.setCheckable(True)
            act.setChecked(abs(self.scale_factor - sc) < 0.01)
            act.triggered.connect(lambda _=False, v=sc: self.set_scale(v))
            size_menu.addAction(act)

        if self.fish.isVisible():
            m.addAction("把鱼藏起来", self.hide_fish)
        else:
            m.addAction("把鱼叫出来", self.show_fish)
        m.addAction("关于大肥鱼", self.show_about)
        m.addSeparator()
        m.addAction("退出", self.quit_all)
        return m

    def show_about(self) -> None:
        box = QMessageBox(self.panel)
        box.setWindowTitle("关于 大肥鱼")
        box.setTextFormat(Qt.RichText)
        box.setText(
            "<b>大肥鱼 · 鲸鱼娘桌宠</b><br><br>"
            "<span style='color:#5A6480'>"
            "双击我 → 打开任务清单<br>"
            "拖我 → 换个位置<br>"
            "点我 → 跟我说说话<br>"
            "右键 → 夸夸频率等设置</span><br><br>"
            "<span style='color:#8A93AA;font-size:11px'>"
            "形象风格参考开源项目 dsh-pet<br>"
            "github.com/PC2005-cloud/dsh-pet<br>"
            "角色素材由 AI 生成，仅供个人学习使用</span>"
        )
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()

    def hide_fish(self) -> None:
        self.bubble.hide()
        self.fish.hide()

    def show_fish(self) -> None:
        self.fish.show()
        self.fish.raise_()
        self.say("我在这儿呢～", 3000)
        self.fish.happy_for(2.0)

    def _set_sound(self, on: bool) -> None:
        self.config["sound"] = bool(on)
        self.save_config()

    def set_scale(self, scale: float) -> None:
        self.scale_factor = float(scale)
        self.config["scale"] = self.scale_factor
        self.save_config()
        self.fish.apply_scale(self.scale_factor)
        self.save_position()
        pos = self.config.get("pos")
        if pos:
            self.fish.move(int(pos[0]), int(pos[1]))
        self.bubble.follow()

    def set_praise_interval(self, mins: int) -> None:
        self.config["praise_minutes"] = mins
        self.save_config()
        self.schedule_praise()
        self.say("好，我调整一下夸你的节奏～", 3000)

    def quit_all(self) -> None:
        self.save_position()
        self.save_tasks()
        self.save_config()
        self.tray.hide()
        self.qapp.quit()


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    QApplication.setApplicationName(APP_NAME)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(make_icon(128))
    QApplication.setStyle("Fusion")

    def hook(tp, val, tb):
        import traceback

        txt = "".join(traceback.format_exception(tp, val, tb))
        try:
            (DATA_DIR / "error.log").write_text(txt, encoding="utf-8")
        except Exception:
            pass
        print(txt, file=sys.stderr, flush=True)

    sys.excepthook = hook

    from PySide6.QtCore import QLockFile
    from PySide6.QtNetwork import QLocalServer, QLocalSocket

    SOCK = "deepseek_pet_single_instance_v2"

    # 锁文件判断是否已有实例（会校验持锁 PID 是否存活，比命名管道可靠）
    lock = QLockFile(str(DATA_DIR / "app.lock"))
    lock.setStaleLockTime(30000)
    if not lock.tryLock(250):
        probe = QLocalSocket()
        probe.connectToServer(SOCK)
        if probe.waitForConnected(300):
            probe.write(b"wake")
            probe.flush()
            probe.waitForBytesWritten(300)
            probe.disconnectFromServer()
        diag("已有实例在运行，本次启动退出")
        return 0

    QLocalServer.removeServer(SOCK)
    server = QLocalServer()
    if not server.listen(SOCK):
        QLocalServer.removeServer(SOCK)
        server.listen(SOCK)

    pet = PetApp(app)
    app._pet = pet  # 保持引用

    def _wake() -> None:
        while server.hasPendingConnections():
            conn = server.nextPendingConnection()
            conn.deleteLater()
        if not pet.fish.isVisible():
            pet.show_fish()
        else:
            pet.say("我已经在啦～", 3000)
            pet.fish.happy_for(2.0)
        pet.fish.raise_()

    server.newConnection.connect(_wake)
    app._server = server

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
