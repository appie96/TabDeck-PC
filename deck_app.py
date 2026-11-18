# deck_app.py — TabDeck PC 프로그램 (설정 창 + 트레이 아이콘 + 서버)
# 실행 전 한 번만: pip install PySide6-Essentials websockets
import asyncio, base64, hashlib, hmac, json, math, os, re, secrets, shutil, socket, struct, subprocess, sys, tempfile, threading, time, uuid, wave, webbrowser
import urllib.error, urllib.request

import websockets
from PySide6.QtCore import Qt, QObject, Signal, QTimer, QSize, QPoint, QPointF, QRect, QRectF, QEvent, QByteArray, QBuffer, QIODevice, QVariantAnimation, QEasingCurve
from PySide6.QtGui import (QIcon, QPixmap, QPainter, QPainterPath, QPen, QColor, QFont, QImage, QImageReader,
                           QKeySequence, QAction, QActionGroup, QFontDatabase, QGuiApplication, QLinearGradient, QRadialGradient)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QPushButton, QToolButton, QComboBox, QButtonGroup,
    QKeySequenceEdit, QStackedWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFrame, QFileDialog,
    QColorDialog, QMessageBox, QSystemTrayIcon, QMenu, QScrollArea, QDialog, QSlider, QLayout, QSizePolicy,
    QListWidget, QDoubleSpinBox,
)

# ───────────── 내장 아이콘 ─────────────
GLYPHS = {   # Lucide 아이콘 (ISC 라이선스, https://lucide.dev)
    "mic": ("마이크", '<path d="M12 19v3" /> <path d="M19 10v2a7 7 0 0 1-14 0v-2" /> <rect x="9" y="2" width="6" height="13" rx="3" />'),
    "mic-off": ("마이크 끔", '<path d="M12 19v3" /> <path d="M15 9.34V5a3 3 0 0 0-5.68-1.33" /> <path d="M16.95 16.95A7 7 0 0 1 5 12v-2" /> <path d="M18.89 13.23A7 7 0 0 0 19 12v-2" /> <path d="m2 2 20 20" /> <path d="M9 9v3a3 3 0 0 0 5.12 2.12" />'),
    "video": ("카메라", '<path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5" /> <rect x="2" y="6" width="14" height="12" rx="2" />'),
    "video-off": ("카메라 끔", '<path d="M10.66 6H14a2 2 0 0 1 2 2v2.5l5.248-3.062A.5.5 0 0 1 22 7.87v8.196" /> <path d="M16 16a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h2" /> <path d="m2 2 20 20" />'),
    "radio": ("방송 시작", '<path d="M16.247 7.761a6 6 0 0 1 0 8.478" /> <path d="M19.075 4.933a10 10 0 0 1 0 14.134" /> <path d="M4.925 19.067a10 10 0 0 1 0-14.134" /> <path d="M7.753 16.239a6 6 0 0 1 0-8.478" /> <circle cx="12" cy="12" r="2" />'),
    "circle-dot": ("녹화", '<circle cx="12" cy="12" r="1" /> <circle cx="12" cy="12" r="10" />'),
    "square": ("정지", '<rect width="18" height="18" x="3" y="3" rx="2" />'),
    "play": ("재생", '<path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z" />'),
    "pause": ("일시정지", '<rect x="14" y="3" width="5" height="18" rx="1" /> <rect x="5" y="3" width="5" height="18" rx="1" />'),
    "clapperboard": ("장면", '<path d="m12.296 3.464 3.02 3.956" /> <path d="M20.2 6 3 11l-.9-2.4c-.3-1.1.3-2.2 1.3-2.5l13.5-4c1.1-.3 2.2.3 2.5 1.3z" /> <path d="M3 11h18v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /> <path d="m6.18 5.276 3.1 3.899" />'),
    "layers": ("소스", '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z" /> <path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12" /> <path d="M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17" />'),
    "monitor": ("화면", '<rect width="20" height="14" x="2" y="3" rx="2" /> <line x1="8" x2="16" y1="21" y2="21" /> <line x1="12" x2="12" y1="17" y2="21" />'),
    "image": ("이미지", '<rect width="18" height="18" x="3" y="3" rx="2" ry="2" /> <circle cx="9" cy="9" r="2" /> <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />'),
    "music": ("음악", '<path d="M21 16V3a1 1 0 0 0-1.28-.96l-10 2.917a1 1 0 0 0-.72.96V19" /> <circle cx="18" cy="16" r="3" /> <circle cx="6" cy="19" r="3" />'),
    "volume-2": ("볼륨", '<path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z" /> <path d="M16 9a5 5 0 0 1 0 6" /> <path d="M19.364 18.364a9 9 0 0 0 0-12.728" />'),
    "volume-x": ("음소거", '<path d="M11 4.702a.7.7 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.7.7 0 0 0 11 19.298z" /> <path d="m16.5 14.5 5-5" /> <path d="m16.5 9.5 5 5" />'),
    "headphones": ("헤드폰", '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3" />'),
    "message-circle": ("채팅", '<path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719" />'),
    "heart": ("하트", '<path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5" />'),
    "star": ("별", '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z" />'),
    "sparkles": ("반짝", '<path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z" /> <path d="M20 2v4" /> <path d="M22 4h-4" /> <circle cx="4" cy="20" r="2" />'),
    "smile": ("웃음", '<path d="M15 10V9" /> <path d="M16.472 15a6 6 0 01-8.943 0" /> <path d="M9 10V9" /> <circle cx="12" cy="12" r="10" />'),
    "laugh": ("폭소", '<path d="M15 10V9" /> <path d="M7.084 14.302a5.12 5.12 0 009.833 0 .24.24 0 00-.235-.302H7.32a.24.24 0 00-.235.302" /> <path d="M9 10V9" /> <circle cx="12" cy="12" r="10" />'),
    "frown": ("슬픔", '<path d="M15 10V9" /> <path d="M9 10V9" /> <path d="M9 16a5 5 0 016 0" /> <circle cx="12" cy="12" r="10" />'),
    "hand": ("손", '<path d="M18 11V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2" /> <path d="M14 10V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v2" /> <path d="M10 10.5V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2v8" /> <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />'),
    "party-popper": ("축하", '<path d="M5.8 11.3 2 22l10.7-3.79" /> <path d="M4 3h.01" /> <path d="M22 8h.01" /> <path d="M15 2h.01" /> <path d="M22 20h.01" /> <path d="m22 2-2.24.75a2.9 2.9 0 0 0-1.96 3.12c.1.86-.57 1.63-1.45 1.63h-.38c-.86 0-1.6.6-1.76 1.44L14 10" /> <path d="m22 13-.82-.33c-.86-.34-1.82.2-1.98 1.11c-.11.7-.72 1.22-1.43 1.22H17" /> <path d="m11 2 .33.82c.34.86-.2 1.82-1.11 1.98C9.52 4.9 9 5.52 9 6.23V7" /> <path d="M11 13c1.93 1.93 2.83 4.17 2 5-.83.83-3.07-.07-5-2-1.93-1.93-2.83-4.17-2-5 .83-.83 3.07.07 5 2Z" />'),
    "zap": ("번개", '<path d="M15.914 4a1.5 1.5 0 00-2.474-1.561l-9 9A1.5 1.5 0 005.5 14h4.002a.5.5 0 01.471.666L8.086 20a1.5 1.5 0 002.475 1.56l9-9A1.5 1.5 0 0018.5 10h-3.997a.5.5 0 01-.472-.667z" />'),
    "bell": ("알림", '<path d="M10.268 21a2 2 0 0 0 3.464 0" /> <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326" />'),
    "timer": ("타이머", '<line x1="10" x2="14" y1="2" y2="2" /> <line x1="12" x2="15" y1="14" y2="11" /> <circle cx="12" cy="14" r="8" />'),
    "gamepad-2": ("게임", '<line x1="6" x2="10" y1="11" y2="11" /> <line x1="8" x2="8" y1="9" y2="13" /> <line x1="15" x2="15.01" y1="12" y2="12" /> <line x1="18" x2="18.01" y1="10" y2="10" /> <path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 0 1 9.828 16h4.344a2 2 0 0 1 1.414.586L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.545-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.151A4 4 0 0 0 17.32 5z" />'),
    "coffee": ("휴식", '<path d="M10 2v2" /> <path d="M14 2v2" /> <path d="M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1h14a4 4 0 1 1 0 8h-1" /> <path d="M6 2v2" />'),
    "moon": ("잠수", '<path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401" />'),
    "eye": ("보기", '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" /> <circle cx="12" cy="12" r="3" />'),
    "eye-off": ("숨기기", '<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49" /> <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242" /> <path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143" /> <path d="m2 2 20 20" />'),
    "globe": ("웹", '<circle cx="12" cy="12" r="10" /> <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" /> <path d="M2 12h20" />'),
    "folder": ("폴더", '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z" />'),
    "settings": ("설정", '<path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915" /> <circle cx="12" cy="12" r="3" />'),
    "power": ("전원", '<path d="M12 2v10" /> <path d="M18.4 6.6a9 9 0 1 1-12.77.04" />'),
    "plus": ("추가", '<path d="M5 12h14" /> <path d="M12 5v14" />'),
}


UI_ICONS = {   # 화면용 아이콘 (버튼 아이콘 목록에는 안 나옴), Lucide
    "copy": '<rect width="14" height="14" x="8" y="8" rx="2" ry="2" /> <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />',
    "refresh-cw": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /> <path d="M21 3v5h-5" /> <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /> <path d="M8 16H3v5" />',
}


# ───────────── 기본 설정 ─────────────
VERSION = "0.1.1"        # exe 파일 정보에도 들어감 (build_exe.py가 읽음). 새로 배포할 때 올리고, GitHub 릴리스 태그도 v0.1.0처럼
UPDATE_REPO = "appie96/TabDeck-PC"   # 새 버전을 확인할 GitHub 저장소 "주인/이름". 비우면 확인 안 함
UPDATE_API = os.environ.get("TABDECK_UPDATE_API", "https://api.github.com")   # 테스트할 땐 가짜 서버로 바꿀 수 있음
UPDATE_EVERY = 24 * 3600 # 자동 확인 간격(초): 하루 한 번
WS_PORT = int(os.environ.get("TABDECK_PORT", 8765))   # 앱과 연결되는 포트 (테스트할 땐 환경 변수로 바꿀 수 있음)
MAX_CONNECTIONS = 16     # 동시에 받을 연결 수 (인증 전 포함). 넘치면 새 연결은 바로 닫음
MAX_MESSAGE = 64 * 1024  # 앱이 보내는 메시지 최대 크기 (앱 메시지는 아주 작음)
DISCOVERY_PORT = 8766    # PC 자동 찾기 신호용 포트
FROZEN = getattr(sys, "frozen", False)                 # exe로 묶어서 실행 중인지
APP_DIR = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))   # 프로그램(.py 또는 .exe)이 있는 폴더
RES_DIR = getattr(sys, "_MEIPASS", APP_DIR)            # exe 안에 같이 묶은 파일(글꼴)이 풀리는 폴더


def _data_dir():
    """설정·이미지 저장 폴더.
    .py로 실행하거나, exe 옆에 deck_config.json이 있으면(휴대용) 프로그램 폴더를 그대로 씀.
    아니면 %APPDATA%\\TabDeck (exe를 Program Files처럼 쓰기 금지된 곳에 둬도 저장되게)"""
    if not FROZEN or os.path.exists(os.path.join(APP_DIR, "deck_config.json")):
        return APP_DIR
    return os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "TabDeck")


BASE_DIR = _data_dir()
CONFIG = os.path.join(BASE_DIR, "deck_config.json")   # 버튼 설정 저장 파일
ICON_DIR = os.path.join(BASE_DIR, "icons")            # 버튼 이미지 저장 폴더 (잘라낸 결과)
SRC_DIR = os.path.join(ICON_DIR, "src")               # 원본 이미지 보관 폴더 (나중에 '위치 조정'용)
MAX_SOURCE = 2400        # 자르기 창에서 다룰 원본의 최대 긴 변(px). 더 크면 줄여서 다룸 (속도용)
IMAGE_SIZE = 256         # 앱으로 보낼 버튼 이미지 크기(px)
GLYPH_SIZE = 128         # 앱으로 보낼 아이콘 크기(px)
TILE = 128               # 설정 창 미리보기 버튼 한 칸 크기(px)

# 색 (밝은 민트 테마)
BG, CARD, LINE = "#eef4f2", "#ffffff", "#e2ebe8"
INK, SUB = "#1f2a44", "#8b95a7"                 # 글자: 짙은 남색 / 보조 회색
MINT, MINT_D, MINT_L = "#8fcfc0", "#4fa898", "#e2f3ef"
DANGER = "#e46f78"
SWATCHES = ["#ffffff", "#e2f3ef", "#a9dccf", "#cfe3f5", "#f6e7c9", "#f8dadb", "#e5dff6", "#3d6b62", "#1f2a44"]
DEFAULT_COLOR = "#ffffff"

ACTION_TYPES = [("run", "프로그램·파일 실행"), ("url", "웹페이지 열기"), ("hotkey", "단축키 보내기"),
                ("group", "여러 개 한꺼번에 실행")]


def text_color_for(bg):
    """버튼 색이 밝으면 남색 글자, 어두우면 흰 글자"""
    c = QColor(bg)
    return INK if (0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()) > 150 else "#ffffff"


def glyph_image(name, color, size):
    """내장 아이콘을 원하는 색과 크기의 그림으로 만듦"""
    body = GLYPHS[name][1] if name in GLYPHS else UI_ICONS[name]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
           f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
    img = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(svg.encode())).render(p)
    p.end()
    return img


def auth_proof(key, role, server_nonce, client_nonce):
    """상호 인증용 증명값. 키 자체는 네트워크로 보내지 않고, 키로 계산한 값만 주고받음.
    role: "app"(앱이 PC에 증명) / "pc"(PC가 앱에 증명). 앱의 DeckAuth.proof와 똑같이 계산해야 함"""
    msg = f"{role}|{server_nonce}|{client_nonce}".encode()
    return hmac.new(key.encode(), msg, hashlib.sha256).hexdigest()


def image_to_b64(img):
    buf = QBuffer()
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return base64.b64encode(bytes(buf.data())).decode()


def render_crop(img, crop, size):
    """원본에서 crop 영역을 잘라 size×size 그림으로 만듦.
    crop = {"cx","cy": 잘라낼 정사각형 중심 (원본 너비·높이 대비 0~1), "zoom": 1이면 짧은 변에 꽉 맞춤}
    zoom이 1보다 작으면 이미지 전체가 들어가고 남는 곳은 투명 (버튼 바탕색이 보임)"""
    w, h = img.width(), img.height()
    side = min(w, h) / crop["zoom"]                    # 잘라낼 정사각형 한 변 (원본 px)
    sel = QRectF(crop["cx"] * w - side / 2, crop["cy"] * h - side / 2, side, side)
    out = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    out.fill(Qt.transparent)
    part = sel.intersected(QRectF(0, 0, w, h)).toAlignedRect()
    if part.isEmpty():
        return out
    s = size / side
    target = QRectF((part.x() - sel.x()) * s, (part.y() - sel.y()) * s, part.width() * s, part.height() * s)
    piece = img.copy(part)
    if s < 1:   # 크게 줄일 땐 미리 부드럽게 줄여 둬야 계단 현상이 안 생김
        piece = piece.scaled(max(1, round(target.width())), max(1, round(target.height())),
                             Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    p = QPainter(out)
    p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    p.drawImage(target, piece)
    p.end()
    return out


# ───────────── 효과음 ─────────────
class Sound:
    """짧고 부드러운 '톡' 소리. 윈도우에서만 재생돼"""
    def __init__(self, store):
        self.store = store
        self.files = {}
        if sys.platform != "win32":
            return
        folder = os.path.join(tempfile.gettempdir(), "tabdeck_sounds")
        os.makedirs(folder, exist_ok=True)
        for kind, notes in {"tick": [(1046, 0, 70)],
                            "done": [(784, 0, 90), (1175, 70, 140)],
                            "fail": [(330, 0, 120), (262, 90, 160)]}.items():
            path = os.path.join(folder, kind + ".wav")
            self._make_wav(path, notes)
            self.files[kind] = path

    @staticmethod
    def _make_wav(path, notes):
        rate = 44100
        total = max(s + d for _, s, d in notes)
        buf = [0.0] * int(rate * total / 1000 + rate * 0.05)
        for freq, start, dur in notes:
            st, ln = int(rate * start / 1000), int(rate * dur / 1000)
            for i in range(ln):
                t = i / rate
                env = min(1.0, i / (rate * 0.004)) * math.exp(-t * 26)
                buf[st + i] += (math.sin(2 * math.pi * freq * t) + 0.25 * math.sin(4 * math.pi * freq * t)) * env * 0.22
        data = struct.pack(f"<{len(buf)}h", *[int(max(-1, min(1, x)) * 32767) for x in buf])
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(data)

    def play(self, kind):
        if not self.store.settings.get("sound", True) or kind not in self.files:
            return
        import winsound
        winsound.PlaySound(self.files[kind], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)


# ───────────── 버튼 동작 실행 ─────────────
# 단축키: 윈도우 SendInput으로 '진짜 키보드 키'(가상 키 번호 + 스캔 코드)를 보냄.
#  예전 방식(pynput)은 글자 키를 '문자 입력'으로 보내서 OBS·Warudo·게임이 단축키로 못 알아들었음
_VK_MODS = {"ctrl": 0x11, "shift": 0x10, "alt": 0x12, "meta": 0x5B, "win": 0x5B}
_VK_NAMES = {
    "esc": 0x1B, "escape": 0x1B, "return": 0x0D, "enter": 0x0D, "space": 0x20, "tab": 0x09,
    "backspace": 0x08, "ins": 0x2D, "insert": 0x2D, "del": 0x2E, "delete": 0x2E,
    "home": 0x24, "end": 0x23, "pgup": 0x21, "pgdown": 0x22, "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "print": 0x2C, "pause": 0x13, "scrolllock": 0x91, "capslock": 0x14, "numlock": 0x90, "menu": 0x5D,
    "media play": 0xB3, "media pause": 0xB3, "toggle media play/pause": 0xB3, "media next": 0xB0,
    "media previous": 0xB1, "media stop": 0xB2, "volume up": 0xAF, "volume down": 0xAE, "volume mute": 0xAD,
}
_VK_NUMPAD = {"*": 0x6A, "+": 0x6B, "-": 0x6D, ".": 0x6E, "/": 0x6F, "enter": 0x0D}
# 확장 키: 스캔 코드에 '확장' 표시가 있어야 숫자 패드 키와 헷갈리지 않음
_VK_EXTENDED = {0x2D, 0x2E, 0x24, 0x23, 0x21, 0x22, 0x25, 0x26, 0x27, 0x28, 0x2C, 0x90, 0x5D, 0x5B, 0x6F}


def parse_hotkey(combo, vk_for_char=None):
    """'ctrl+shift+f1' / 'ctrl+num+5' / 'media play' → (보조 키 번호 목록, 키 번호, 확장 키 여부)"""
    s = (combo or "").strip().lower()
    if not s:
        raise ValueError("단축키가 비어 있어")
    if s.endswith("+") and len(s) > 1:            # 마지막 키가 '+' 자체인 경우 (ctrl++)
        tokens = [t.strip() for t in s[:-1].rstrip("+").split("+") if t.strip()] + ["+"]
    else:
        tokens = [t.strip() for t in s.split("+")]
    *mods, key = tokens
    numpad = "num" in mods
    vks = []
    for m in mods:
        if m == "num":
            continue
        if m not in _VK_MODS:
            raise ValueError(f"모르는 보조 키: {m}")
        if _VK_MODS[m] not in vks:
            vks.append(_VK_MODS[m])
    ext = False
    if numpad and (key.isdigit() and len(key) == 1):
        vk = 0x60 + int(key)
    elif numpad and key in _VK_NUMPAD:
        vk = _VK_NUMPAD[key]
        ext = key in ("enter", "/")
    elif key in _VK_NAMES:
        vk = _VK_NAMES[key]
    elif re.fullmatch(r"f([1-9]|1\d|2[0-4])", key):
        vk = 0x70 + int(key[1:]) - 1
    elif len(key) == 1 and ("a" <= key <= "z" or "0" <= key <= "9"):
        vk = ord(key.upper())
    elif len(key) == 1 and vk_for_char:
        code = vk_for_char(key)                   # 현재 키보드 배열에서 이 문자가 어느 키인지 (+Shift 필요 여부)
        if code is None:
            raise ValueError(f"이 키보드에서 찾을 수 없는 키: {key}")
        vk, need_shift = code
        if need_shift and 0x10 not in vks:        # Qt가 Shift+1을 'shift+!'로 적는 경우 등
            vks.append(0x10)
    else:
        raise ValueError(f"모르는 키: {key}")
    return vks, vk, ext or vk in _VK_EXTENDED


def _win_vk_for_char(ch):
    import ctypes
    r = ctypes.windll.user32.VkKeyScanW(ord(ch))
    if r == -1 or (r & 0xFF) == 0xFF:
        return None
    return r & 0xFF, bool(r & 0x100)


def _foreground_is_admin_only():
    """앞에 있는 창이 관리자 권한으로 실행 중이고 TabDeck은 아니면 True (윈도우가 키 입력을 몰래 막음)"""
    import ctypes
    from ctypes import wintypes
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return False
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value or pid.value == os.getpid():
            return False
        k32, adv = ctypes.windll.kernel32, ctypes.windll.advapi32
        hp = k32.OpenProcess(0x1000, False, pid.value)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not hp:
            return False
        tok = wintypes.HANDLE()
        try:
            if not adv.OpenProcessToken(hp, 0x0008, ctypes.byref(tok)):   # TOKEN_QUERY
                return True                                       # 토큰을 못 열면 관리자 프로그램일 가능성이 큼
            elev, size = wintypes.DWORD(), wintypes.DWORD()
            adv.GetTokenInformation(tok, 20, ctypes.byref(elev), 4, ctypes.byref(size))   # TokenElevation
            k32.CloseHandle(tok)
            return bool(elev.value)
        finally:
            k32.CloseHandle(hp)
    except Exception:
        return False


def _win_send(vks, vk, ext, hold=0.06):
    import ctypes
    from ctypes import wintypes
    ULONG_PTR = ctypes.c_size_t

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]

    class _U(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("u", _U)]

    user32 = ctypes.windll.user32
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    user32.MapVirtualKeyW.restype = wintypes.UINT

    def one(code, up, extended):
        flags = (0x0001 if extended else 0) | (0x0002 if up else 0)      # EXTENDEDKEY, KEYUP
        inp = INPUT(type=1)
        inp.u.ki = KEYBDINPUT(code, user32.MapVirtualKeyW(code, 0) & 0xFF, flags, 0, 0)
        if user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)) != 1:
            raise OSError("윈도우가 키 입력을 막았어")

    pressed = []
    try:
        for m in vks:                               # 보조 키부터 차례로 누름
            one(m, False, m == 0x5B)
            pressed.append((m, m == 0x5B))
            time.sleep(0.015)
        one(vk, False, ext)
        pressed.append((vk, ext))
        time.sleep(hold)                            # 잠깐 누르고 있어야 OBS처럼 키 상태를 살피는 프로그램도 알아챔
    finally:
        for code, extended in reversed(pressed):   # 중간에 실패해도 눌린 키는 꼭 뗌
            one(code, True, extended)
            time.sleep(0.015)


def send_hotkey(combo):
    """'ctrl+shift+f1' 같은 글자를 실제 키보드 입력으로 바꿔서 누름"""
    if sys.platform != "win32":
        raise ValueError("단축키 보내기는 윈도우에서만 돼")
    vks, vk, ext = parse_hotkey(combo, _win_vk_for_char)
    if _foreground_is_admin_only():
        raise ValueError("지금 앞에 있는 창이 관리자 권한으로 실행 중이라 윈도우가 단축키를 막아. "
                         "TabDeck도 관리자 권한으로 실행하거나, 그 프로그램을 일반 권한으로 실행해 줘")
    _win_send(vks, vk, ext)


def open_target(target):
    """프로그램·파일 경로, 웹 주소, 명령어를 알맞은 방법으로 열기"""
    target = target.strip()
    if re.match(r"(?i)https?://", target):
        webbrowser.open(target)
    elif hasattr(os, "startfile") and os.path.exists(target):
        os.startfile(target)                        # 파일·프로그램 경로면 윈도우 방식으로 열기
    else:
        subprocess.Popen(target, shell=True)        # 그 외에는 명령어로 실행


def run_action(b):
    t, cmd = b.get("type", "run"), b.get("cmd", "").strip()
    if t == "group":
        items = [s.strip() for s in b.get("group", []) if s and s.strip()]
        if not items:
            raise ValueError("그룹에 실행할 게 없어")
        gap = min(max(float(b.get("gap", 0.5) or 0), 0.0), 10.0)
        fails = []
        for i, item in enumerate(items):
            if i and gap:
                time.sleep(gap)                     # 프로그램끼리 부딪히지 않게 조금씩 간격
            try:
                open_target(item)
            except Exception as e:
                fails.append(f"{os.path.basename(item) or item} ({e})")
        if fails:
            raise ValueError(f"{len(items)}개 중 {len(fails)}개 실패: " + ", ".join(fails))
        return
    if not cmd:
        raise ValueError("실행할 내용이 비어 있어")
    if t == "run":
        open_target(cmd)
    elif t == "url":
        webbrowser.open(cmd)
    elif t == "hotkey":
        send_hotkey(cmd)
    else:
        raise ValueError("모르는 동작: " + t)


def local_ips():
    """PC에 연결된 모든 네트워크(랜선, Wi-Fi)의 IP"""
    ips = set()
    try:
        ips |= {i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)}
    except OSError:
        pass
    try:                                    # 위 방법으로 못 찾을 때를 위한 예비 방법
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(ip for ip in ips if not ip.startswith("127.") and not ip.startswith("169.254."))


# ───────────── 설정 저장소 ─────────────
class Store:
    def __init__(self):
        self.lock = threading.RLock()
        self._payload = []
        os.makedirs(SRC_DIR, exist_ok=True)
        data = {}
        if os.path.exists(CONFIG):
            with open(CONFIG, encoding="utf-8") as f:
                data = json.load(f)
        data.setdefault("key", secrets.token_urlsafe(6))
        data.setdefault("buttons", [])
        data.setdefault("settings", {})
        data["settings"].setdefault("sound", True)      # 효과음은 처음엔 켜짐
        data["settings"].setdefault("glass", True)      # 유리 효과 (가짜 유리라 가벼움)
        data["settings"].setdefault("motion", "off")    # 배경 움직임: off / eco / smooth
        data["settings"].setdefault("update_check", True)   # 새 버전 알림 (하루 한 번 버전 번호만 물어봄)
        for b in data["buttons"]:                        # 예전 설정 파일도 그대로 읽히게
            b.setdefault("type", "run"); b.setdefault("cmd", "")
            b.setdefault("group", []); b.setdefault("gap", 0.5)   # 그룹 실행: 열 것 목록, 사이 간격(초)
            b.setdefault("color", DEFAULT_COLOR); b.setdefault("icon", ""); b.setdefault("glyph", "")
            b.setdefault("src", ""); b.setdefault("crop", None)   # 원본 파일 이름, 마지막 자르기 위치
            if b["color"].lower() == "#2a2b36":         # 예전 버전의 어두운 기본색은 새 기본색으로
                b["color"] = DEFAULT_COLOR
        self.data = data
        self.save()

    @property
    def key(self):
        return self.data["key"]

    def new_key(self):
        """비밀 키 재발급"""
        with self.lock:
            self.data["key"] = secrets.token_urlsafe(6)
            self.save()
            return self.data["key"]

    @property
    def buttons(self):
        return self.data["buttons"]

    @property
    def settings(self):
        return self.data["settings"]

    def save(self):
        with self.lock:
            tmp = CONFIG + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, CONFIG)

    def get(self, bid):
        with self.lock:
            return next((dict(b) for b in self.buttons if b["id"] == bid), None)

    def update(self, bid, **fields):
        with self.lock:
            for b in self.buttons:
                if b["id"] == bid:
                    b.update(fields)

    def add(self):
        with self.lock:
            b = {"id": "b" + uuid.uuid4().hex[:6], "label": "새 버튼", "type": "run", "cmd": "",
                 "color": DEFAULT_COLOR, "icon": "", "glyph": "star", "src": "", "crop": None}
            self.buttons.append(b)
            return b["id"]

    def remove(self, bid):
        with self.lock:
            self.data["buttons"] = [b for b in self.buttons if b["id"] != bid]

    def move(self, bid, step):
        with self.lock:
            lst = self.buttons
            i = next(i for i, b in enumerate(lst) if b["id"] == bid)
            j = max(0, min(len(lst) - 1, i + step))
            lst.insert(j, lst.pop(i))

    @staticmethod
    def read_image(path):
        """이미지 읽기. 폰 사진의 회전 정보도 반영하고, 너무 크면 다루기 좋은 크기로 줄임"""
        r = QImageReader(path)
        r.setAutoTransform(True)
        img = r.read()
        if img.isNull():
            return None
        if max(img.width(), img.height()) > MAX_SOURCE:
            img = img.scaled(MAX_SOURCE, MAX_SOURCE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return img

    def import_source(self, path, bid):
        """고른 원본을 icons/src/에 그대로 복사해 둠 (다시 자를 때 씀)"""
        if self.read_image(path) is None:
            raise ValueError("이미지를 읽을 수 없어")
        ext = os.path.splitext(path)[1].lower() or ".png"
        name = f"{bid}-{uuid.uuid4().hex[:6]}{ext}"
        shutil.copyfile(path, os.path.join(SRC_DIR, name))
        return name

    def adopt_icon_as_source(self, bid):
        """원본이 없는 예전 버튼: 지금 버튼 그림을 원본으로 삼음"""
        b = self.get(bid)
        p = self.image_path(b["icon"])
        if not p:
            return ""
        name = f"{bid}-{uuid.uuid4().hex[:6]}.png"
        shutil.copyfile(p, os.path.join(SRC_DIR, name))
        return name

    def save_crop(self, bid, img, crop):
        """잘라낸 결과를 버튼 이미지로 저장 (새 이름이라 기기 쪽에서도 바뀐 게 확실히 반영됨)"""
        name = f"{bid}-{uuid.uuid4().hex[:6]}.png"
        render_crop(img, crop, IMAGE_SIZE).save(os.path.join(ICON_DIR, name), "PNG")
        return name

    def drop_file(self, folder, name):
        """더 이상 어떤 버튼도 안 쓰는, 이 프로그램이 만든 이미지 파일 정리"""
        if not name or os.path.basename(name) != name:
            return
        with self.lock:
            key = "icon" if folder == ICON_DIR else "src"
            if any(b.get(key) == name for b in self.buttons):
                return
        try:
            os.remove(os.path.join(folder, name))
        except OSError:
            pass

    def image_path(self, name):
        p = os.path.join(ICON_DIR, name) if name else ""
        return p if p and os.path.exists(p) else ""

    def source_path(self, name):
        p = os.path.join(SRC_DIR, name) if name else ""
        return p if p and os.path.exists(p) else ""

    def rebuild(self):
        """앱으로 보낼 버튼 목록을 미리 만들어 둠 (설정 창 쪽에서만 호출)"""
        items = []
        with self.lock:
            for b in self.buttons:
                tc = text_color_for(b["color"])
                d = {"id": b["id"], "label": b["label"], "color": b["color"], "text": tc, "mode": "none", "icon": ""}
                p = self.image_path(b["icon"])
                if p:
                    with open(p, "rb") as f:
                        d["mode"], d["icon"] = "image", base64.b64encode(f.read()).decode()
                elif b["glyph"] in GLYPHS:
                    d["mode"], d["icon"] = "glyph", image_to_b64(glyph_image(b["glyph"], tc, GLYPH_SIZE))
                items.append(d)
            self._payload = items

    def payload(self):
        with self.lock:
            return list(self._payload)


# ───────────── 서버 (백그라운드에서 돌아감) ─────────────
def parse_version(text):
    """'v1.2.3' / '1.2' → (1, 2, 3) / (1, 2, 0). 숫자 버전이 아니면 None"""
    m = re.fullmatch(r"v?(\d+)(?:\.(\d+))?(?:\.(\d+))?", (text or "").strip())
    return tuple(int(x or 0) for x in m.groups()) if m else None


class Updater(QObject):
    """GitHub 최신 릴리스의 버전 번호만 확인 (파일을 받거나 설치하지는 않음)"""
    done = Signal(object)     # {"ok":True,"version","url","newer"} 또는 {"ok":False,"msg"}

    def check(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        if not UPDATE_REPO:
            self.done.emit({"ok": False, "msg": "확인할 주소가 아직 설정되지 않았어"})
            return
        try:
            req = urllib.request.Request(f"{UPDATE_API}/repos/{UPDATE_REPO}/releases/latest",
                                         headers={"Accept": "application/vnd.github+json",
                                                  "User-Agent": f"TabDeck/{VERSION}"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read(256 * 1024).decode("utf-8"))
            latest = parse_version(data.get("tag_name", ""))
            if latest is None:
                raise ValueError("버전 형식이 이상해")
            # 받은 주소가 우리 저장소 페이지가 아니면 쓰지 않고 정해진 주소로 (엉뚱한 사이트로 안내하지 않게)
            page = f"https://github.com/{UPDATE_REPO}/releases/latest"
            url = data.get("html_url", "")
            if not url.startswith(f"https://github.com/{UPDATE_REPO}/"):
                url = page
            self.done.emit({"ok": True, "version": ".".join(map(str, latest)), "url": url,
                            "newer": latest > parse_version(VERSION)})
        except urllib.error.HTTPError as e:
            self.done.emit({"ok": False, "msg": "아직 올라온 릴리스가 없어" if e.code == 404 else f"서버 응답 {e.code}"})
        except (ValueError, AttributeError, TypeError):
            self.done.emit({"ok": False, "msg": "릴리스의 버전 정보를 읽지 못했어 (태그는 v0.2.0 형식)"})
        except Exception as e:
            self.done.emit({"ok": False, "msg": f"인터넷 연결을 확인해 줘 ({type(e).__name__})"})


class Bridge(QObject):
    """서버 쪽 소식을 설정 창으로 안전하게 전달하는 통로"""
    clients_changed = Signal(int)
    pressed = Signal(str, bool)       # 기기에서 누른 버튼 id, 성공 여부
    log = Signal(str)
    error = Signal(str)


class DeckServer:
    def __init__(self, store, bridge):
        self.store, self.bridge = store, bridge
        self.clients = set()
        self.active = 0          # 인증 전 연결까지 포함한 현재 연결 수
        self.loop = None

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._main())
        except OSError as e:
            self.bridge.error.emit(
                f"포트 {WS_PORT}를 열 수 없어.\n다른 TabDeck(예전 deck_server.py나 .py로 켠 창)이 켜져 있으면 닫고 다시 실행해 줘.\n\n({e})")

    async def _main(self):
        async with websockets.serve(self._guarded, "0.0.0.0", WS_PORT, ping_interval=10, max_size=MAX_MESSAGE):
            await self._announce()

    async def _guarded(self, ws):
        """연결 수 제한: 같은 네트워크에서 연결을 잔뜩 열어 PC를 느리게 만드는 걸 막음"""
        if self.active >= MAX_CONNECTIONS:
            await ws.close(1013, "too many connections")
            return
        self.active += 1
        try:
            await self._handle(ws)
        finally:
            self.active -= 1

    async def _auth(self, ws, ip):
        """상호 인증. 성공하면 True.
        PC → 앱  {"type":"challenge","nonce":서버난수}
        앱 → PC  {"type":"hello","cnonce":앱난수,"proof":auth_proof(key,"app",...)}
        PC → 앱  {"type":"welcome","proof":auth_proof(key,"pc",...)}   ← 앱은 이걸로 진짜 PC인지 확인"""
        key = self.store.key
        snonce = secrets.token_hex(16)
        await ws.send(json.dumps({"type": "challenge", "nonce": snonce}))
        hello = json.loads(await asyncio.wait_for(ws.recv(), 5))
        if not isinstance(hello, dict) or hello.get("type") != "hello":
            raise ValueError("not hello")
        if "proof" not in hello:          # 키를 그대로 보내는 예전 앱
            self.bridge.log.emit(f"연결 거절 · {ip} — 예전 버전 앱이야. 새 앱을 설치해 줘")
            await ws.send(json.dumps({"type": "error", "msg": "앱을 새 버전으로 업데이트해 줘"}, ensure_ascii=False))
            return False
        cnonce, proof = str(hello.get("cnonce", "")), str(hello.get("proof", ""))
        expect = auth_proof(key, "app", snonce, cnonce)
        if not (16 <= len(cnonce) <= 128) or not hmac.compare_digest(proof.encode(), expect.encode()):
            await asyncio.sleep(1)        # 틀렸을 때 잠깐 쉬어서 마구 시도하기 어렵게
            self.bridge.log.emit(f"연결 거절 · {ip} — 비밀 키가 틀렸어")
            await ws.send(json.dumps({"type": "error", "msg": "비밀 키가 틀렸어"}, ensure_ascii=False))
            return False
        await ws.send(json.dumps({"type": "welcome", "proof": auth_proof(key, "pc", snonce, cnonce)}))
        return True

    def kick_all(self, msg):
        """연결된 모든 기기에 알리고 끊음 (비밀 키를 새로 만들었을 때)"""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._kick_all(msg), self.loop)

    async def _kick_all(self, msg):
        for ws in list(self.clients):
            try:
                await ws.send(json.dumps({"type": "error", "msg": msg}, ensure_ascii=False))
                await ws.close()
            except Exception:
                pass

    async def _send_buttons(self, ws):
        await ws.send(json.dumps({"type": "buttons", "items": self.store.payload()}, ensure_ascii=False))

    async def _handle(self, ws):
        ip = ws.remote_address[0] if ws.remote_address else "알 수 없는 기기"
        try:
            if not await self._auth(ws, ip):
                return
            self.clients.add(ws)
            self.bridge.clients_changed.emit(len(self.clients))
            self.bridge.log.emit(f"기기 연결됨 · {ip}")
            await self._send_buttons(ws)
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except ValueError:                # 이상한 메시지 하나 때문에 연결을 끊지 않음
                    self.bridge.log.emit(f"알 수 없는 메시지 무시 · {ip}")
                    continue
                if not isinstance(msg, dict) or msg.get("type") != "press":
                    continue
                b = self.store.get(msg.get("id"))
                ok = False
                if b:
                    try:
                        # 실행은 따로 빼서 돌림: 프로그램이 늦게 열려도 다른 기기 입력이 안 멈추게
                        await asyncio.get_running_loop().run_in_executor(None, run_action, b)
                        ok = True
                        self.bridge.log.emit(f"실행 · {b['label']}")
                    except Exception as e:
                        self.bridge.log.emit(f"실패 · {b['label']} — {e}")
                    self.bridge.pressed.emit(b["id"], ok)
                await ws.send(json.dumps({"type": "result", "id": msg.get("id"), "ok": ok}))
        except asyncio.TimeoutError:
            self.bridge.log.emit(f"연결 거절 · {ip} — 5초 안에 인사(hello)가 안 왔어")
        except websockets.exceptions.ConnectionClosedOK:
            pass                                  # 앱이 정상적으로 닫음 (아래에서 '연결 끊김'으로 표시)
        except websockets.exceptions.ConnectionClosedError as e:
            code = e.rcvd.code if e.rcvd else "응답 없음"
            self.bridge.log.emit(f"연결 끊김 · {ip} — 신호가 갑자기 끊겼어 (Wi-Fi·절전 확인, 코드 {code})")
            ip = None                             # 아래에서 한 번 더 쓰지 않게
        except ValueError:
            self.bridge.log.emit(f"연결 거절 · {ip} — 첫 메시지를 읽을 수 없어 (TabDeck 앱이 아닌 것 같아)")
        except Exception as e:
            self.bridge.log.emit(f"연결 오류 · {ip} — {type(e).__name__}: {e}")
            ip = None
        finally:
            if ws in self.clients:
                self.clients.discard(ws)
                self.bridge.clients_changed.emit(len(self.clients))
                if ip:
                    self.bridge.log.emit(f"기기 연결 끊김 · {ip}")

    def broadcast(self):
        """설정이 바뀌면 연결된 모든 기기에 새 버튼 목록을 보냄"""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(), self.loop)

    async def _broadcast(self):
        for ws in list(self.clients):
            try:
                await self._send_buttons(ws)
            except Exception:
                pass

    async def _announce(self):
        msg = f"DECK:{WS_PORT}".encode()
        while True:
            for ip in local_ips():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    s.bind((ip, 0))
                    s.sendto(msg, (ip.rsplit(".", 1)[0] + ".255", DISCOVERY_PORT))
                    s.close()
                except OSError:
                    pass
            await asyncio.sleep(2)


# ───────────── 화면 스타일 ─────────────
def build_style(glass=False):
    """화면 스타일. glass=True면 큰 카드가 반투명해져서 뒤 배경이 비침 (가짜 유리: 실시간 블러 없음)"""
    panel_bg = "rgba(255,255,255,0.66)" if glass else CARD
    panel_line = "rgba(255,255,255,0.9)" if glass else "#e6eeeb"
    return f"""
QDialog#root {{ background:{BG}; }}
QWidget {{ color:{INK}; font-family:'Pretendard','Noto Sans KR','Malgun Gothic','Segoe UI',sans-serif; font-size:13px; }}
QFrame#panel, QFrame#topbar {{ background:{panel_bg}; border:1px solid {panel_line}; border-bottom:2px solid #dbe6e2; border-radius:24px; }}
QFrame#hero {{ background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eaf6f2, stop:1 #f6faf9); border:none; border-radius:20px; }}
QFrame#sub {{ background:#f7faf9; border:1px solid #edf2f0; border-radius:18px; }}
QLineEdit#heroName {{ font-size:16px; font-weight:bold; background:white; }}
QLabel#group {{ background:{BG}; border-radius:14px; padding:6px 12px; color:{SUB}; }}
QToolButton#icon {{ background:transparent; border:none; border-radius:10px; padding:4px; }}
QToolButton#icon:hover {{ background:{MINT_L}; }}
QLabel {{ background:transparent; }}
QMenu {{ background:white; border:1px solid {LINE}; padding:6px; }}
QMenu::item {{ color:{INK}; background:transparent; padding:9px 26px 9px 30px; border-radius:8px; font-size:14px; }}
QMenu::item:selected {{ background:{MINT_L}; color:{INK}; }}
QMenu::item:disabled {{ color:{SUB}; }}
QMenu::separator {{ height:1px; background:{LINE}; margin:5px 10px; }}
QMenu::indicator {{ width:14px; height:14px; left:10px; }}
QLabel#section {{ color:{SUB}; font-size:12px; font-weight:bold; }}
QLabel#hint {{ color:{SUB}; font-size:12px; }}
QLabel#log {{ color:{SUB}; font-size:12px; }}
QLabel#pill {{ background:{BG}; border-radius:14px; padding:7px 12px; }}
QListWidget#group {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; padding:4px; outline:none; }}
QListWidget#group::item {{ padding:6px 8px; border-radius:8px; color:{INK}; }}
QListWidget#group::item:selected {{ background:{MINT_L}; color:{INK}; }}
QDoubleSpinBox {{ background:{CARD}; border:1px solid {LINE}; border-radius:10px; padding:5px 8px; }}
QLineEdit, QComboBox, QKeySequenceEdit {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; padding:8px 11px; }}
QLineEdit:focus, QComboBox:focus {{ border:1px solid {MINT}; }}
QComboBox::drop-down {{ border:none; width:26px; }}
QComboBox QAbstractItemView {{ background:{CARD}; border:1px solid {LINE}; selection-background-color:{MINT_L}; selection-color:{INK}; outline:none; }}
QPushButton {{ background:{BG}; border:1px solid {LINE}; border-radius:12px; padding:8px 14px; }}
QPushButton:hover {{ background:{MINT_L}; border-color:{MINT}; }}
QPushButton:pressed {{ background:{MINT}; padding-top:9px; padding-bottom:7px; }}
QPushButton:disabled {{ color:#b8c0cc; background:{BG}; border-color:{LINE}; }}
QPushButton#primary {{ background:{MINT}; border:none; color:white; font-weight:bold; font-size:14px; padding:11px 14px; border-radius:16px; }}
QPushButton#primary:hover {{ background:#9fd8cb; }}
QPushButton#primary:pressed {{ background:{MINT_D}; padding-top:12px; padding-bottom:10px; }}
QPushButton#primary[state="busy"] {{ background:#b5e0d6; }}
QPushButton#primary[state="ok"] {{ background:{MINT_D}; }}
QPushButton#primary[state="fail"] {{ background:{DANGER}; }}
QPushButton#danger {{ background:{CARD}; color:{DANGER}; border:1px solid #f3d3d6; }}
QPushButton#danger:hover {{ background:#fdf0f1; }}
QPushButton#seg {{ background:{BG}; border:none; border-radius:11px; padding:7px 0; color:{SUB}; }}
QPushButton#seg:checked {{ background:{CARD}; color:{INK}; font-weight:bold; border:1px solid {LINE}; }}
QPushButton#ghost {{ background:transparent; border:none; color:{SUB}; padding:6px 8px; }}
QPushButton#ghost:hover {{ color:{MINT_D}; }}
QPushButton#ghost:checked {{ color:{MINT_D}; }}
QToolButton#glyph {{ background:transparent; border:1px solid transparent; border-radius:10px; }}
QToolButton#glyph:hover {{ background:{MINT_L}; }}
QToolButton#glyph:checked {{ background:{MINT_L}; border:1px solid {MINT}; }}
QScrollArea {{ border:none; background:transparent; }}
QScrollArea > QWidget > QWidget {{ background:transparent; }}
QScrollBar:vertical {{ background:transparent; width:8px; margin:4px; }}
QScrollBar::handle:vertical {{ background:#d5dfdc; border-radius:3px; min-height:30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height:0; }}
QWidget#page {{ background:transparent; }}
QStackedWidget {{ background:transparent; }}
QSlider::groove:horizontal {{ height:6px; background:{LINE}; border-radius:3px; }}
QSlider::sub-page:horizontal {{ background:{MINT}; border-radius:3px; }}
QSlider::handle:horizontal {{ background:white; border:2px solid {MINT_D}; width:16px; height:16px; margin:-7px 0; border-radius:10px; }}
QSlider::handle:horizontal:hover {{ background:{MINT_L}; }}
"""


STYLE = build_style()
MOTION_MS = {"off": 0, "eco": 125, "smooth": 16}    # 배경 움직임: 멈춤 / 절전(초당 8번) / 부드럽게(초당 60번)


class Backdrop(QWidget):
    """창 전체 배경: 은은한 그라데이션 + 흐릿한 색 덩어리 3개.
    덩어리는 블러 계산 없이 '가운데 진하고 가장자리 투명한 원'으로 그려서 가벼움"""
    BLOBS = [  # 색, 기준 위치(가로·세로 비율), 크기(짧은 변 대비), 움직임 속도
        (QColor(143, 207, 192), 0.12, 0.10, 0.75, 0.11, 0.08),
        (QColor(246, 193, 200), 0.92, 0.35, 0.60, 0.09, 0.12),
        (QColor(188, 215, 242), 0.45, 1.00, 0.70, 0.07, 0.10),
    ]

    def __init__(self):
        super().__init__(objectName="root")
        self.t = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def set_motion(self, mode):
        ms = MOTION_MS.get(mode, 0)
        self.timer.stop()
        if ms:
            self.timer.start(ms)

    def _tick(self):
        if not self.isVisible():          # 트레이로 숨어 있을 땐 그리지 않음
            return
        self.t += self.timer.interval() / 1000
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        g = QLinearGradient(0, 0, w, h)
        g.setColorAt(0, QColor("#f4f9f7"))
        g.setColorAt(0.55, QColor("#eaf3f0"))
        g.setColorAt(1, QColor("#e1ece9"))
        p.fillRect(self.rect(), g)
        p.setPen(Qt.NoPen)
        for col, bx, by, size, sx, sy in self.BLOBS:
            cx = w * (bx + 0.08 * math.sin(self.t * sx * 2 * math.pi / 3))
            cy = h * (by + 0.08 * math.cos(self.t * sy * 2 * math.pi / 3))
            r = min(w, h) * size
            rg = QRadialGradient(QPointF(cx, cy), r)
            c0 = QColor(col); c0.setAlpha(150)
            c1 = QColor(col); c1.setAlpha(0)
            rg.setColorAt(0, c0)
            rg.setColorAt(1, c1)
            p.setBrush(rg)
            p.drawEllipse(QPointF(cx, cy), r, r)


def app_icon(size=64):
    """민트 바탕에 흰 칸 4개. size를 키우면 같은 모양을 더 크게 그림 (exe 아이콘용)"""
    return QIcon(app_icon_pixmap(size))


def app_icon_pixmap(size=64):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(size / 64, size / 64)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(MINT))
    p.drawRoundedRect(4, 4, 56, 56, 16, 16)
    p.setBrush(QColor("white"))
    for r in range(2):
        for c in range(2):
            p.drawRoundedRect(15 + c * 19, 15 + r * 19, 15, 15, 5, 5)
    p.end()
    return pm


# ───────────── 버튼 미리보기 한 칸 (직접 그리는 위젯) ─────────────
class FlowLayout(QLayout):
    """칸이 모자라면 다음 줄로 넘기는 배치 (창이 좁아져도 오른쪽이 잘리지 않게)"""
    def __init__(self, parent=None, spacing=4):
        super().__init__(parent)
        self._items = []
        self._gap = spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item): self._items.append(item)
    def count(self): return len(self._items)
    def itemAt(self, i): return self._items[i] if 0 <= i < len(self._items) else None
    def takeAt(self, i): return self._items.pop(i) if 0 <= i < len(self._items) else None
    def expandingDirections(self): return Qt.Orientations()
    def hasHeightForWidth(self): return True
    def heightForWidth(self, w): return self._place(QRect(0, 0, w, 0), move=False)
    def sizeHint(self): return self.minimumSize()

    def minimumSize(self):
        # 가장 넓은 칸 하나만 들어가면 됨 (나머지는 아래 줄로)
        s = QSize()
        for it in self._items:
            s = s.expandedTo(it.minimumSize())
        m = self.contentsMargins()
        return s + QSize(m.left() + m.right(), m.top() + m.bottom())

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._place(rect, move=True)

    def _place(self, rect, move):
        m = self.contentsMargins()
        r = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y, line_h = r.x(), r.y(), 0
        for it in self._items:
            if it.widget() is not None and not it.widget().isVisibleTo(it.widget().parentWidget()):
                continue
            sz = it.sizeHint()
            if x + sz.width() > r.right() + 1 and line_h > 0:
                x, y, line_h = r.x(), y + line_h + self._gap, 0
            if move:
                it.setGeometry(QRect(QPoint(x, y), sz))
            x += sz.width() + self._gap
            line_h = max(line_h, sz.height())
        return y + line_h - rect.y() + m.bottom()


class ElideLabel(QLabel):
    """폭이 모자라면 뒤를 …로 줄여 보여주는 한 줄 글자 (전체 내용은 마우스를 올리면 보임)"""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._full = ""
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setMinimumWidth(1)

    def setText(self, text):
        self._full = text
        self.setToolTip(text)
        self._refit()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._refit()

    def _refit(self):
        super().setText(self.fontMetrics().elidedText(self._full, Qt.ElideRight, max(10, self.width())))


class Tile(QWidget):
    """마우스를 올리면 떠오르고, 누르면 쑥 들어가며 민트빛이 퍼지는 버튼"""
    clicked = Signal()

    def __init__(self, add=False, sound=None):
        super().__init__()
        self.add, self.sound = add, sound
        self.setFixedSize(TILE, TILE)
        self.setCursor(Qt.PointingHandCursor)
        self.b, self.img, self.glyph, self.selected = None, None, None, False
        self.lift = self.press = self.ripple = self.badge = self.fail = 0.0
        self.ripple_pos = QPointF(64, 64)
        self._anims = {}

    def set_button(self, b, store):
        self.b = b
        p = store.image_path(b["icon"])
        self.img = QImage(p) if p else None
        tc = text_color_for(b["color"])
        self.glyph = glyph_image(b["glyph"], tc, 96) if (not self.img and b["glyph"] in GLYPHS) else None
        # 그림자 색: 버튼 색(이미지면 평균색)을 어둡게 해서 씀 → 버튼마다 자기 색 그림자
        base = QColor(self.img.scaled(1, 1, Qt.IgnoreAspectRatio, Qt.SmoothTransformation).pixel(0, 0)) if self.img \
            else QColor(b["color"])
        self.shadow = base.darker(260 if base.lightness() > 200 else 170)
        self.update()

    # 애니메이션 도우미: 어떤 값을 부드럽게 바꾸면서 다시 그림
    def _anim(self, attr, end, ms, curve=QEasingCurve.OutCubic, start=None):
        old = self._anims.get(attr)
        if old:
            old.stop()
        a = QVariantAnimation(self)
        a.setStartValue(float(getattr(self, attr) if start is None else start))
        a.setEndValue(float(end))
        a.setDuration(ms)
        a.setEasingCurve(curve)
        a.valueChanged.connect(lambda v, attr=attr: (setattr(self, attr, v), self.update()))
        self._anims[attr] = a
        a.start()

    def enterEvent(self, e):
        self._anim("lift", 1, 200)

    def leaveEvent(self, e):
        self._anim("lift", 0, 260)
        if self.press:
            self._anim("press", 0, 220)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        self.ripple_pos = e.position()
        self._anim("press", 1, 90)
        self._anim("ripple", 1, 560, start=0)
        if self.sound:
            self.sound.play("tick")

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        self._anim("press", 0, 380, QEasingCurve.OutBack)
        if self.rect().contains(e.position().toPoint()):
            self.clicked.emit()

    def play_result(self, ok):
        """실행 결과 표시: 성공이면 체크가 톡 떴다 사라지고, 실패면 흔들리며 붉어짐"""
        if ok:
            self._anim("badge", 1, 1300, QEasingCurve.Linear, start=0)
        else:
            self._anim("fail", 1, 520, QEasingCurve.Linear, start=0)

    def paintEvent(self, e):
        if not self.add and self.b is None:
            return      # 아직 보여줄 버튼이 없음 (버튼 0개일 때 편집 패널 미리보기). 그리다가 에러 나면 프로그램이 통째로 꺼짐
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        r = QRectF(self.rect()).adjusted(10, 10, -10, -10)
        radius = 24
        shake = math.sin(self.fail * math.pi * 6) * 6 * (1 - self.fail) if 0 < self.fail < 1 else 0
        dy = -3 * self.lift + 2 * self.press
        scale = 1 - 0.05 * self.press

        c = r.center()
        p.translate(c + QPointF(shake, dy))
        p.scale(scale, scale)
        p.translate(-c)
        # 부드러운 그림자 (떠오를수록 진하고 넓게, 버튼과 같이 줄어듦)
        strength = 0.7 + 0.8 * self.lift - 0.5 * self.press
        sy = 3 + 4 * self.lift - 2 * self.press
        p.setPen(Qt.NoPen)
        sh = getattr(self, "shadow", QColor(31, 42, 68)) if not self.add else QColor(31, 42, 68)
        for i in range(10):
            col = QColor(sh)
            col.setAlpha(int(max(0.0, strength) * (10 - i) * (1.1 if self.add else 1.35)))
            p.setBrush(col)
            p.drawRoundedRect(r.adjusted(-i + 1, -i + sy + 2, i - 1, i + sy + 2), radius + i, radius + i)
        path = QPainterPath()
        path.addRoundedRect(r, radius, radius)

        if self.add:
            pen = QPen(QColor(MINT_D if self.lift > 0.5 else "#c9d6d2"), 1.6, Qt.DashLine)
            p.setPen(pen)
            p.setBrush(QColor(CARD))
            p.drawPath(path)
            p.drawImage(QRectF(c.x() - 14, c.y() - 22, 28, 28), glyph_image("plus", MINT_D, 56))
            p.setPen(QColor(SUB))
            p.setFont(self._font(11))
            p.drawText(QRectF(r.left(), c.y() + 10, r.width(), 20), Qt.AlignCenter, "버튼 추가")
            return

        b = self.b
        tc = QColor(text_color_for(b["color"]))
        # 바탕: 단색 대신 위가 살짝 밝은 세로 그라데이션
        base = QColor(b["color"])
        bg = QLinearGradient(r.topLeft(), r.bottomLeft())
        bg.setColorAt(0, base.lighter(106) if base.lightness() < 245 else base)
        bg.setColorAt(1, base.darker(104))
        p.fillPath(path, bg)
        p.save()
        p.setClipPath(path)
        if self.glyph:   # 아이콘 뒤 은은한 원
            ring = QColor(tc)
            ring.setAlpha(26 if tc.name() == INK else 38)
            p.setPen(Qt.NoPen)
            p.setBrush(ring)
            p.drawEllipse(QPointF(c.x(), r.top() + 42), 28, 28)
        if self.img:
            p.drawImage(r, self.img)                                  # 이미지가 버튼 전체를 덮음
            g = QLinearGradient(r.left(), r.top() + r.height() * 0.45, r.left(), r.bottom())
            g.setColorAt(0, QColor(15, 22, 38, 0))
            g.setColorAt(1, QColor(15, 22, 38, 170))
            p.fillRect(r, g)
            p.setPen(QColor("white"))
            p.setFont(self._font(11, True))
            p.drawText(r.adjusted(12, 0, -12, -10), Qt.AlignBottom | Qt.AlignLeft,
                       p.fontMetrics().elidedText(b["label"], Qt.ElideRight, int(r.width() - 24)))
        elif self.glyph:
            p.drawImage(QRectF(c.x() - 22, r.top() + 20, 44, 44), self.glyph)
            p.setPen(tc)
            p.setFont(self._font(11, True))
            p.drawText(QRectF(r.left() + 8, r.top() + 70, r.width() - 16, 22), Qt.AlignCenter,
                       p.fontMetrics().elidedText(b["label"], Qt.ElideRight, int(r.width() - 16)))
        else:
            p.setPen(tc)
            p.setFont(self._font(13, True))
            p.drawText(r.adjusted(10, 10, -10, -10), Qt.AlignCenter | Qt.TextWordWrap, b["label"])

        # 누른 자리에서 퍼지는 민트빛
        if 0 < self.ripple < 1:
            pos = (self.ripple_pos - c - QPointF(shake, dy)) / scale + c
            rad = 150 * self.ripple
            col = QColor(MINT)
            col.setAlpha(int(150 * (1 - self.ripple)))
            p.setPen(Qt.NoPen)
            p.setBrush(col)
            p.drawEllipse(pos, rad, rad)
        if 0 < self.fail < 1:
            p.fillRect(r, QColor(228, 111, 120, int(110 * (1 - self.fail))))
        # 위쪽 가장자리 빛 반사 (살짝 볼록한 느낌)
        edge = QLinearGradient(r.topLeft(), r.bottomLeft())
        edge.setColorAt(0, QColor(255, 255, 255, 150 if not self.img else 90))
        edge.setColorAt(0.35, QColor(255, 255, 255, 0))
        p.setPen(QPen(edge, 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(r.adjusted(1, 1, -1, -1), radius - 1, radius - 1)
        p.restore()

        # 테두리: 선택된 버튼은 바깥쪽 민트 링, 밝은 버튼은 옅은 선
        if self.selected:
            p.setPen(QPen(QColor(MINT_D), 2.2))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(r.adjusted(-4, -4, 4, 4), radius + 4, radius + 4)
        if tc.name() == INK and not self.img:
            p.setPen(QPen(QColor(LINE), 1))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)

        # 성공 체크 배지
        if 0 < self.badge < 1:
            v = self.badge
            alpha = min(1.0, v * 7) * min(1.0, (1 - v) * 4)
            pop = 0.6 + 0.4 * min(1.0, v * 7) + 0.12 * math.sin(min(1.0, v * 7) * math.pi)
            bc = QPointF(r.right() - 18, r.top() + 18)
            p.setOpacity(alpha)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(MINT_D))
            p.drawEllipse(bc, 13 * pop, 13 * pop)
            pen = QPen(QColor("white"), 2.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            p.setPen(pen)
            s = pop
            p.drawPolyline([bc + QPointF(-5.5 * s, 0.5 * s), bc + QPointF(-1.5 * s, 4.5 * s), bc + QPointF(6 * s, -4 * s)])
            p.setOpacity(1)

    def _font(self, size, bold=False):
        f = QFont(self.font())
        f.setPointSize(size)
        f.setBold(bold)
        return f


# ───────────── 이미지 자르기 ─────────────
class CropView(QWidget):
    """정사각형 틀은 가운데 고정, 이미지를 드래그로 옮기고 휠로 확대·축소"""
    changed = Signal()
    MARGIN = 34

    def __init__(self, img, color, crop=None):
        super().__init__()
        self.img, self.color = img, QColor(color)
        self.setMinimumSize(420, 420)
        self.setCursor(Qt.OpenHandCursor)
        w, h = img.width(), img.height()
        self.short = min(w, h)
        self.zmin = self.short / max(w, h)                  # 이미지 전체가 틀 안에 들어오는 배율
        self.zmax = max(1.0, min(10.0, self.short / 32))    # 원본 32px보다 작게는 안 들어감
        self.drag, self.dragging = None, False
        c = crop or {}
        self.zoom = max(self.zmin, min(self.zmax, float(c.get("zoom", 1.0))))
        self.cx, self.cy = float(c.get("cx", 0.5)) * w, float(c.get("cy", 0.5)) * h   # 틀 중심 (원본 px)
        self._clamp()

    def crop(self):
        return {"cx": round(self.cx / self.img.width(), 5), "cy": round(self.cy / self.img.height(), 5),
                "zoom": round(self.zoom, 5)}

    def side(self):
        return self.short / self.zoom             # 틀에 들어가는 원본 한 변 길이 (px)

    def frame(self):
        s = min(self.width(), self.height()) - 2 * self.MARGIN
        return QRectF((self.width() - s) / 2, (self.height() - s) / 2, s, s)

    def scale(self):
        return self.frame().width() / self.side()   # 화면 px / 원본 px

    def _clamp(self):
        """틀 밖으로 빈 곳이 생기지 않게 (이미지가 틀보다 작을 땐 틀 안에서만 움직이게)"""
        half = self.side() / 2
        for attr, size in (("cx", self.img.width()), ("cy", self.img.height())):
            lo, hi = sorted((half, size - half))
            setattr(self, attr, max(lo, min(hi, getattr(self, attr))))

    def set_zoom(self, z, anchor=None):
        """배율 바꾸기. anchor(화면 위치)에 있던 지점이 그 자리에 머물게 함"""
        z = max(self.zmin, min(self.zmax, z))
        fc = self.frame().center()
        a = anchor if anchor is not None else fc
        s1 = self.scale()
        px, py = self.cx + (a.x() - fc.x()) / s1, self.cy + (a.y() - fc.y()) / s1
        self.zoom = z
        s2 = self.scale()
        self.cx, self.cy = px - (a.x() - fc.x()) / s2, py - (a.y() - fc.y()) / s2
        self._clamp()
        self.update()
        self.changed.emit()

    def reset(self, z=1.0):
        self.cx, self.cy = self.img.width() / 2, self.img.height() / 2
        self.set_zoom(z)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag, self.dragging = e.position(), True
            self.setCursor(Qt.ClosedHandCursor)
            self.update()

    def mouseMoveEvent(self, e):
        if self.drag is None:
            return
        d = e.position() - self.drag
        self.drag = e.position()
        s = self.scale()
        self.cx -= d.x() / s
        self.cy -= d.y() / s
        self._clamp()
        self.update()
        self.changed.emit()

    def mouseReleaseEvent(self, e):
        self.drag, self.dragging = None, False
        self.setCursor(Qt.OpenHandCursor)
        self.update()

    def mouseDoubleClickEvent(self, e):
        self.reset()

    def wheelEvent(self, e):
        steps = e.angleDelta().y() / 120
        if steps:
            self.set_zoom(self.zoom * (1.12 ** steps), e.position())
        e.accept()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        outer = QPainterPath()
        outer.addRoundedRect(QRectF(self.rect()), 16, 16)
        p.setClipPath(outer)
        p.fillRect(self.rect(), QColor("#dde7e4"))

        f, s = self.frame(), self.scale()
        radius = f.width() * 24 / 108                      # 실제 버튼과 같은 둥근 정도
        frame = QPainterPath()
        frame.addRoundedRect(f, radius, radius)
        p.fillPath(frame, self.color)                      # 이미지가 작을 때 보일 버튼 바탕색
        fc = f.center()
        p.drawImage(QRectF(fc.x() - self.cx * s, fc.y() - self.cy * s,
                           self.img.width() * s, self.img.height() * s), self.img)

        veil = QPainterPath()                              # 틀 바깥은 뿌옇게
        veil.addRect(QRectF(self.rect()))
        p.fillPath(veil.subtracted(frame), QColor(238, 244, 242, 200))

        if self.dragging:                                  # 움직이는 동안만 3분할 안내선
            p.save()
            p.setClipPath(frame)
            p.setPen(QPen(QColor(255, 255, 255, 150), 1))
            for i in (1, 2):
                x = f.left() + f.width() * i / 3
                y = f.top() + f.height() * i / 3
                p.drawLine(QPointF(x, f.top()), QPointF(x, f.bottom()))
                p.drawLine(QPointF(f.left(), y), QPointF(f.right(), y))
            p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("white"), 3))
        p.drawPath(frame)
        p.setPen(QPen(QColor(MINT_D), 1.4))
        p.drawPath(frame)


class AboutDialog(QDialog):
    """버전, 새 버전 확인, 라이선스"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("root")
        self.setWindowTitle("TabDeck 정보")
        self.setFixedWidth(380)
        self.url = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 22, 24, 20)
        lay.setSpacing(10)
        top = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(app_icon_pixmap(56))
        top.addWidget(logo)
        top.addSpacing(8)
        name = QLabel(f"<span style='font-size:20px;font-weight:800;color:{INK}'>Tab</span>"
                      f"<span style='font-size:20px;font-weight:300;color:{MINT_D}'>Deck</span>"
                      f"<br><span style='color:{SUB}'>버전 {VERSION}</span>")
        top.addWidget(name, 1)
        lay.addLayout(top)
        self.status = QLabel(objectName="hint")
        self.status.setWordWrap(True)
        self.set_status("새 버전 확인을 눌러 봐" if UPDATE_REPO else "새 버전 확인 주소가 아직 설정되지 않았어")
        lay.addWidget(self.status)
        row = QHBoxLayout()
        self.check_btn = QPushButton("새 버전 확인")
        self.check_btn.setEnabled(bool(UPDATE_REPO))
        self.get_btn = QPushButton("받기 페이지 열기", objectName="primary")
        self.get_btn.hide()
        self.get_btn.clicked.connect(lambda: self.url and webbrowser.open(self.url))
        row.addWidget(self.check_btn)
        row.addWidget(self.get_btn)
        row.addStretch()
        lay.addLayout(row)
        lic = QLabel("아이콘: Lucide (ISC 라이선스)\n글꼴: Pretendard (SIL Open Font License 1.1)", objectName="hint")
        lay.addSpacing(6)
        lay.addWidget(lic)
        close = QPushButton("닫기", objectName="ghost")
        close.clicked.connect(self.accept)
        lay.addWidget(close, 0, Qt.AlignRight)

    def set_status(self, text):
        self.status.setText(text)

    def show_result(self, res):
        self.check_btn.setEnabled(bool(UPDATE_REPO))
        if not res.get("ok"):
            self.set_status(f"확인하지 못했어: {res.get('msg', '')}")
        elif res.get("newer"):
            self.url = res["url"]
            self.set_status(f"새 버전 {res['version']}이 나왔어! 받기 페이지에서 TabDeck.exe를 받아서 지금 파일과 바꾸면 돼.")
            self.get_btn.show()
        else:
            self.set_status(f"지금이 최신 버전이야 (최신 {res['version']})")


class CropDialog(QDialog):
    """버튼에 보일 부분 고르기 창"""
    def __init__(self, parent, img, button, crop=None, note=""):
        super().__init__(parent)
        self.setObjectName("root")
        self.setWindowTitle("보일 부분 고르기")
        self.img = img
        self.view = CropView(img, button["color"], crop)
        self._syncing = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 18)
        lay.setSpacing(14)
        lay.addWidget(QLabel("<span style='font-size:17px;font-weight:bold'>보일 부분 고르기</span>"))

        body = QHBoxLayout()
        body.setSpacing(18)
        body.addWidget(self.view, 1)

        side = QVBoxLayout()
        side.setSpacing(8)
        side.addWidget(QLabel("미리보기", objectName="section"))
        self.preview = Tile()
        self.preview.b = {"label": button["label"], "color": button["color"]}
        self.preview.setCursor(Qt.ArrowCursor)
        side.addWidget(self.preview, 0, Qt.AlignLeft)
        side.addSpacing(6)
        tips = QLabel("드래그 · 위치 옮기기<br>휠 · 확대 / 축소<br>더블클릭 · 처음 상태로", objectName="hint")
        side.addWidget(tips)
        if note:
            n = QLabel(note, objectName="hint")
            n.setWordWrap(True)
            n.setStyleSheet(f"color:{MINT_D};")
            side.addWidget(n)
        side.addStretch()
        fill_btn = QPushButton("꽉 채우기")
        fill_btn.clicked.connect(lambda: self.view.reset(1.0))
        fit_btn = QPushButton("전체 보기")
        fit_btn.setToolTip("이미지 전체가 들어가고, 남는 곳은 버튼 바탕색으로 보여")
        fit_btn.clicked.connect(lambda: self.view.reset(self.view.zmin))
        fit_btn.setEnabled(self.view.zmin < 0.999)
        side.addWidget(fill_btn)
        side.addWidget(fit_btn)
        side_w = QWidget(objectName="page")
        side_w.setFixedWidth(170)
        side_w.setLayout(side)
        body.addWidget(side_w)
        lay.addLayout(body, 1)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)
        small, big = QLabel(), QLabel()
        small.setPixmap(QPixmap.fromImage(glyph_image("image", SUB, 28)).scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        big.setPixmap(QPixmap.fromImage(glyph_image("image", SUB, 44)).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setCursor(Qt.PointingHandCursor)
        self.slider.setEnabled(self.view.zmax > self.view.zmin)
        self.slider.valueChanged.connect(self._on_slider)
        bottom.addWidget(small)
        bottom.addWidget(self.slider, 1)
        bottom.addWidget(big)
        bottom.addSpacing(24)
        cancel = QPushButton("취소")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("적용", objectName="primary")
        ok.setMinimumWidth(110)
        ok.setCursor(Qt.PointingHandCursor)
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        bottom.addWidget(cancel)
        bottom.addWidget(ok)
        lay.addLayout(bottom)

        self.view.changed.connect(self._sync)
        self.resize(760, 560)
        self._sync()

    # 슬라이더는 배율을 로그 눈금으로 (확대할수록 천천히 커지게)
    def _z_to_t(self, z):
        v = self.view
        return 0 if v.zmax <= v.zmin else round(1000 * math.log(z / v.zmin) / math.log(v.zmax / v.zmin))

    def _on_slider(self, t):
        if self._syncing:
            return
        v = self.view
        v.set_zoom(v.zmin * (v.zmax / v.zmin) ** (t / 1000))

    def _sync(self):
        self._syncing = True
        self.slider.setValue(self._z_to_t(self.view.zoom))
        self._syncing = False
        self.preview.img = render_crop(self.img, self.view.crop(), IMAGE_SIZE)
        self.preview.update()

    def crop(self):
        return self.view.crop()


# ───────────── 메인 창 ─────────────
class MainWindow(QMainWindow):
    test_finished = Signal(bool, str)     # 'PC에서 테스트' 결과 (실행은 다른 스레드에서)

    def __init__(self, store, server, bridge):
        super().__init__()
        self.store, self.server = store, server
        self.sound = Sound(store)
        self.selected = None
        self.loading = False
        self.icon_view = "glyph"
        self.testing = False
        self.tiles = {}
        self.tray_hint_shown = False

        self.setWindowTitle("TabDeck")
        self.setWindowIcon(app_icon())
        self.resize(1120, 780)

        # 저장·전송은 0.4초 모아서 한 번에 (타자 칠 때마다 보내지 않게)
        self.save_timer = QTimer(self, singleShot=True, interval=400)
        self.save_timer.timeout.connect(self._save_and_push)

        self.backdrop = root = Backdrop()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)
        outer.addWidget(self._build_topbar())
        body = QHBoxLayout()
        body.setSpacing(16)
        body.addWidget(self._build_grid_panel(), 3)
        body.addWidget(self._build_editor_panel(), 2)
        outer.addLayout(body, 1)
        self.setCentralWidget(root)

        bridge.clients_changed.connect(self._on_clients)
        bridge.log.connect(self.log_label.setText)
        bridge.pressed.connect(lambda bid, ok: self.tiles[bid].play_result(ok) if bid in self.tiles else None)
        bridge.error.connect(lambda t: QMessageBox.critical(self, "TabDeck", t))

        self.store.rebuild()
        self._build_tray()
        self.refresh_grid()
        self.select(self.store.buttons[0]["id"] if self.store.buttons else None)
        self._apply_look()                 # 저장된 유리 효과·배경 움직임 설정 적용
        self.test_finished.connect(self._on_test_finished)
        # 새 버전 확인 (켜고 5초 뒤, 하루 한 번)
        self.latest, self.about = None, None
        self.updater = Updater(self)
        self.updater.done.connect(self._on_update)
        self.tray.messageClicked.connect(lambda: self.latest and webbrowser.open(self.latest["url"]))
        QTimer.singleShot(5000, self._auto_update_check)
        # 편집 패널은 내용이 들어갈 만큼은 항상 확보 (창을 줄이면 왼쪽 버튼 격자가 먼저 좁아짐)
        sc = self.editor_scroll
        sc.setMinimumWidth(sc.widget().minimumSizeHint().width() + sc.verticalScrollBar().sizeHint().width() + 4)

    # ── 위쪽 상태 표시줄 ──
    def _build_topbar(self):
        bar = QFrame(objectName="topbar")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(22, 14, 16, 14)
        lay.setSpacing(8)
        title = QLabel(f"<span style='font-size:20px;font-weight:800;color:{INK}'>Tab</span>"
                       f"<span style='font-size:20px;font-weight:300;color:{MINT_D}'>Deck</span>")
        self.conn_label = QLabel(objectName="pill")
        self._on_clients(0)
        ips = local_ips()
        self.ips = ips
        self.ip_label = ip_label = QLabel(f"<span style='color:{SUB}'>PC IP</span>&nbsp; " + (" / ".join(ips) if ips else "확인 불가"),
                                          objectName="pill")
        ip_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        ip_label.setMinimumWidth(1)        # 창 최소 폭에 IP 길이를 넣지 않음 (넉넉하면 다 보이고, 좁으면 접힘)
        # 비밀 키는 평소엔 가려 둠 (방송 화면에 그대로 나가지 않게). 눈 버튼을 누르면 15초 동안만 보임
        self.key_label = QLabel(objectName="pill")
        self.key_label.setTextFormat(Qt.RichText)
        self.key_btn = QToolButton(objectName="glyph", checkable=True)
        self.key_btn.setFixedSize(34, 34)
        self.key_btn.setIconSize(QSize(18, 18))
        self.key_btn.setCursor(Qt.PointingHandCursor)
        self.key_btn.toggled.connect(self._show_key)
        self.key_hide_timer = QTimer(self, singleShot=True, interval=15000)
        self.key_hide_timer.timeout.connect(lambda: self.key_btn.setChecked(False))
        self._show_key(False)
        self.copy_btn = QPushButton("키 복사")
        self.copy_btn.clicked.connect(self._copy_key)
        self.new_key_btn = QPushButton("새 키", objectName="ghost")
        self.new_key_btn.setToolTip("비밀 키를 새로 만들어. 연결된 기기는 모두 끊기고 새 키를 넣어야 해")
        self.new_key_btn.clicked.connect(self._new_key)
        self.sound_btn = QPushButton(objectName="ghost", checkable=True)
        self.sound_btn.setChecked(self.store.settings.get("sound", True))
        self.sound_btn.toggled.connect(self._toggle_sound)
        self._paint_sound_btn()
        # 접속 정보는 캡슐 하나로 묶고, 버튼은 아이콘만
        def icon_btn(name, tip, slot):
            b = QToolButton(objectName="icon")
            b.setIcon(QIcon(QPixmap.fromImage(glyph_image(name, SUB, 36))))
            b.setIconSize(QSize(17, 17))
            b.setFixedSize(30, 30)
            b.setToolTip(tip)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(slot)
            return b
        self.key_btn.setObjectName("icon")
        self.key_btn.setFixedSize(30, 30)
        self.copy_btn = icon_btn("copy", "키 복사", self._copy_key)
        self.new_key_btn = icon_btn("refresh-cw", "새 키 만들기", self._new_key)
        cap = QFrame()
        cap.setStyleSheet(f"QFrame {{ background:{BG}; border-radius:17px; }} QLabel {{ background:transparent; padding:0; }}")
        cl = QHBoxLayout(cap)
        cl.setContentsMargins(14, 3, 6, 3)
        cl.setSpacing(6)
        ip_label.setObjectName("")
        self.key_label.setObjectName("")
        self.ip_div = divider = QFrame()
        divider.setStyleSheet(f"background:{LINE}; margin:0 6px;")   # 가운데 1px 선, 양옆 6px 여백
        divider.setFixedSize(13, 16)
        # 창이 좁으면 IP 글자 대신 보이는 작은 버튼 (마우스를 올리면 IP, 누르면 복사 메뉴)
        self.ip_btn = icon_btn("monitor", "PC IP: " + (" / ".join(ips) if ips else "확인 불가"), self._ip_menu)
        self.ip_btn.hide()
        cl.addWidget(ip_label)
        cl.addWidget(self.ip_btn)
        cl.addWidget(divider)
        cl.addWidget(self.key_label)
        cl.addWidget(self.key_btn)
        cl.addWidget(self.copy_btn)
        cl.addWidget(self.new_key_btn)
        self.sound_btn.setText("")
        self.sound_btn.setToolTip("효과음")
        self.sound_btn.setFixedSize(38, 38)
        self.conn_label.setStyleSheet(f"background:{MINT_L}; color:{INK}; border-radius:15px; padding:7px 14px;")
        lay.addWidget(title)
        lay.addSpacing(14)
        lay.addWidget(self.conn_label)
        lay.addStretch()
        lay.addWidget(cap)
        lay.addSpacing(4)
        lay.addWidget(self.sound_btn)
        lay.addWidget(self._build_look_menu())
        self.topbar = bar
        self.topbar_full_w = 0          # IP를 다 보여줄 때 필요한 폭 (펼친 상태일 때마다 다시 잼)
        bar.installEventFilter(self)
        return bar

    # 상단 바 폭이 모자라면 IP 글자를 접고 아이콘 버튼으로 (넉넉해지면 다시 펼침)
    def eventFilter(self, obj, e):
        if obj is getattr(self, "topbar", None) and e.type() == QEvent.Resize:
            QTimer.singleShot(0, self._fit_topbar)
        return super().eventFilter(obj, e)

    def _fit_topbar(self):
        bar = self.topbar
        if not self.ip_btn.isVisible():
            # IP 글자는 최소 폭 계산에서 빠져 있으니, 그 글자 폭을 더한 만큼이 '다 보여줄 때' 필요한 폭
            self.topbar_full_w = bar.minimumSizeHint().width() + self.ip_label.sizeHint().width() + 6
        compact = bar.width() < self.topbar_full_w
        if compact != self.ip_btn.isVisible():
            self.ip_label.setVisible(not compact)
            self.ip_btn.setVisible(compact)

    def _ip_menu(self):
        menu = QMenu(self)
        if not self.ips:
            menu.addAction("IP를 확인할 수 없어").setEnabled(False)
        for ip in self.ips:
            menu.addAction(f"{ip}  복사", lambda ip=ip: (QGuiApplication.clipboard().setText(ip),
                                                         self.log_label.setText(f"IP {ip} 복사했어")))
        menu.exec(self.ip_btn.mapToGlobal(self.ip_btn.rect().bottomLeft()))

    # ── 화면 꾸미기 메뉴 (유리 효과, 배경 움직임) ──
    def _build_look_menu(self):
        btn = QToolButton(objectName="icon")
        btn.setIcon(QIcon(QPixmap.fromImage(glyph_image("sparkles", SUB, 40))))
        btn.setIconSize(QSize(19, 19))
        btn.setFixedSize(38, 38)
        btn.setToolTip("화면 꾸미기")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setPopupMode(QToolButton.InstantPopup)
        btn.setStyleSheet("QToolButton::menu-indicator { image:none; width:0; }")
        menu = QMenu(btn)
        glass = QAction("유리 효과", menu, checkable=True)
        glass.setChecked(self.store.settings.get("glass", True))
        glass.toggled.connect(lambda on: self._set_look("glass", on))
        menu.addAction(glass)
        menu.addSeparator()
        menu.addSection("배경 움직임")
        group = QActionGroup(menu)
        for key, name in [("off", "멈춤"), ("eco", "천천히 (절전)"), ("smooth", "부드럽게 (전기 조금 더 씀)")]:
            a = QAction(name, menu, checkable=True)
            a.setChecked(self.store.settings.get("motion", "off") == key)
            a.triggered.connect(lambda _=False, k=key: self._set_look("motion", k))
            group.addAction(a)
            menu.addAction(a)
        # ── 정보·업데이트 ──
        menu.addSeparator()
        self.update_act = QAction("", menu)          # 새 버전이 있을 때만 보임
        self.update_act.setVisible(False)
        self.update_act.triggered.connect(lambda: webbrowser.open(self.latest["url"]))
        menu.addAction(self.update_act)
        notify = QAction("새 버전 알림 받기", menu, checkable=True)
        notify.setChecked(self.store.settings.get("update_check", True))
        notify.toggled.connect(self._set_update_check)
        menu.addAction(notify)
        menu.addAction(f"TabDeck 정보 (버전 {VERSION})", self.show_about)
        btn.setMenu(menu)
        btn.setToolTip("화면 꾸미기 · 정보")
        self.look_btn = btn
        return btn

    # ── 새 버전 확인 ──
    def _set_update_check(self, on):
        self.store.settings["update_check"] = on
        self.store.save()

    def _auto_update_check(self):
        """켤 때 한 번: 알림이 켜져 있고 마지막 확인이 하루 지났으면 조용히 확인"""
        s = self.store.settings
        if not UPDATE_REPO or not s.get("update_check", True):
            return
        if time.time() - float(s.get("update_last", 0) or 0) < UPDATE_EVERY:
            return
        self.updater.check()

    def _on_update(self, res):
        if res.get("ok"):                     # 확인에 성공했을 때만 결과를 바꿈 (실패하면 이전 결과 유지)
            self.store.settings["update_last"] = time.time()
            self.store.save()
            self.latest = res if res.get("newer") else None
            if not self.latest:
                self.update_act.setVisible(False)
                self.look_btn.setIcon(QIcon(QPixmap.fromImage(glyph_image("sparkles", SUB, 40))))
                self.look_btn.setToolTip("화면 꾸미기 · 정보")
        if res.get("ok") and self.latest:
            v = self.latest["version"]
            self.update_act.setText(f"새 버전 {v} 받기 →")
            self.update_act.setVisible(True)
            self.look_btn.setIcon(QIcon(QPixmap.fromImage(glyph_image("sparkles", MINT_D, 40))))
            self.look_btn.setToolTip(f"새 버전 {v}이 나왔어")
            self.log_label.setText(f"새 버전 {v}이 나왔어 · 오른쪽 위 반짝 메뉴에서 받을 수 있어")
            if self.store.settings.get("update_notified") != v:      # 같은 버전은 한 번만 알림
                self.store.settings["update_notified"] = v
                self.store.save()
                if self.tray.isVisible():
                    self.tray.showMessage("TabDeck", f"새 버전 {v}이 나왔어. 눌러서 받기 페이지 열기",
                                          QSystemTrayIcon.Information, 6000)
        if self.about is not None:
            self.about.show_result(res)

    def show_about(self):
        self.about = AboutDialog(self)
        self.about.check_btn.clicked.connect(self._manual_check)
        if self.latest:
            self.about.show_result(self.latest)
        self.about.exec()
        self.about = None

    def _manual_check(self):
        self.about.set_status("확인하는 중...")
        self.about.check_btn.setEnabled(False)
        self.updater.check()

    def _set_look(self, field, value):
        self.store.settings[field] = value
        self.store.save()
        self._apply_look()

    def _apply_look(self):
        QApplication.instance().setStyleSheet(build_style(self.store.settings.get("glass", True)))
        self.backdrop.set_motion(self.store.settings.get("motion", "off"))
        self.backdrop.update()

    def _show_key(self, show):
        key = self.store.key if show else "•" * 8
        self.key_label.setText(f"<span style='color:{SUB}'>비밀 키</span>&nbsp; {key}")
        self.key_label.setTextInteractionFlags(Qt.TextSelectableByMouse if show else Qt.NoTextInteraction)
        self.key_btn.setIcon(QIcon(QPixmap.fromImage(glyph_image("eye-off" if show else "eye", MINT_D if show else SUB, 36))))
        self.key_btn.setToolTip("키 가리기" if show else "키 보기 (15초 뒤 다시 가려져)")
        if show:
            self.key_hide_timer.start()
        else:
            self.key_hide_timer.stop()

    def _new_key(self):
        if QMessageBox.question(
                self, "TabDeck",
                "비밀 키를 새로 만들까?\n\n연결된 기기는 모두 끊기고, 각 기기에 새 키를 다시 넣어야 해.\n"
                "키가 남에게 보였을 것 같을 때 쓰면 돼.") != QMessageBox.Yes:
            return
        self.store.new_key()
        self.server.kick_all("PC에서 비밀 키를 새로 만들었어. 새 키를 넣어 줘")
        self.key_btn.setChecked(True)          # 새 키를 바로 보여 줌 (15초 뒤 자동으로 가려짐)
        self._show_key(True)
        self.log_label.setText("비밀 키를 새로 만들었어 · 기기마다 새 키를 넣어 줘")

    def _on_clients(self, n):
        dot = MINT_D if n else "#c3ccd6"
        self.conn_label.setText(f"<span style='color:{dot}'>●</span>&nbsp; 연결된 기기 <b>{n}</b>대")

    def _copy_key(self):
        QGuiApplication.clipboard().setText(self.store.key)
        self.copy_btn.setText("복사됨 ✓")
        QTimer.singleShot(1200, lambda: self.copy_btn.setText("키 복사"))

    def _toggle_sound(self, on):
        self.store.settings["sound"] = on     # 끄면 다시 켤 때까지 저장돼서 유지
        self.store.save()
        self._paint_sound_btn()
        if on:
            self.sound.play("tick")

    def _paint_sound_btn(self):
        on = self.sound_btn.isChecked()
        self.sound_btn.setIcon(QIcon(QPixmap.fromImage(glyph_image("volume-2" if on else "volume-x",
                                                                   MINT_D if on else SUB, 40))))
        self.sound_btn.setText("")

    # ── 왼쪽: 버튼 미리보기 격자 ──
    def _build_grid_panel(self):
        panel = QFrame(objectName="panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(22, 18, 22, 16)
        head = QHBoxLayout()
        head.addWidget(QLabel(f"<span style='font-size:17px;font-weight:bold'>내 버튼</span>"))
        head.addStretch()
        head.addWidget(QLabel("클릭해서 편집 · 기기에서 누르면 여기서도 반응해", objectName="hint"))
        lay.addLayout(head)
        holder = QWidget()
        self.grid = QGridLayout(holder)
        self.grid.setSpacing(4)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_scroll.setWidget(holder)
        lay.addWidget(self.grid_scroll, 1)
        self.columns = 4
        self.log_label = QLabel("아직 기록이 없어", objectName="log")
        self.log_label.setTextFormat(Qt.PlainText)    # 버튼 이름 등에 HTML이 섞여도 글자 그대로 표시
        lay.addWidget(self.log_label)
        return panel

    def refresh_grid(self):
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w:
                w.deleteLater()
        self.tiles = {}
        items = list(self.store.buttons)
        for i, b in enumerate(items):
            t = Tile(sound=self.sound)
            t.set_button(b, self.store)
            t.selected = b["id"] == self.selected
            t.clicked.connect(lambda bid=b["id"]: self.select(bid))
            self.grid.addWidget(t, i // self.columns, i % self.columns)
            self.tiles[b["id"]] = t
        add = Tile(add=True, sound=self.sound)
        add.clicked.connect(self.add_button)
        n = len(items)
        self.grid.addWidget(add, n // self.columns, n % self.columns)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cols = max(1, (self.grid_scroll.viewport().width() - 8) // (TILE + 4))
        if cols != self.columns:            # 창 너비가 바뀌면 한 줄 칸 수를 다시 맞춤
            self.columns = cols
            self.refresh_grid()

    # ── 오른쪽: 편집 패널 ──
    def _build_editor_panel(self):
        panel = QFrame(objectName="panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(6, 6, 6, 6)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(8)
        scroll.setWidget(inner)
        pl.addWidget(scroll)
        self.editor_scroll = scroll
        outer = lay
        outer.setSpacing(12)

        # 맨 위: 선택한 버튼을 크게 보여주는 카드
        hero = QFrame(objectName="hero")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(8, 8, 18, 8)
        hl.setSpacing(10)
        self.hero_tile = Tile()
        self.hero_tile.setCursor(Qt.ArrowCursor)
        hl.addWidget(self.hero_tile)
        hv = QVBoxLayout()
        hv.setSpacing(6)
        hv.addStretch()
        hv.addWidget(QLabel("이름", objectName="section"))
        self.name_edit = QLineEdit(objectName="heroName")
        self.name_edit.setMinimumWidth(130)    # 창이 좁아도 이름 몇 글자는 보이게
        self.name_edit.textEdited.connect(lambda t: self._set("label", t))
        hv.addWidget(self.name_edit)
        self.hero_sub = ElideLabel(objectName="hint")
        hv.addWidget(self.hero_sub)
        hv.addStretch()
        hl.addLayout(hv, 1)
        outer.addWidget(hero)

        card1 = QFrame(objectName="sub")
        lay = QVBoxLayout(card1)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)
        outer.addWidget(card1)
        lay.addWidget(QLabel("버튼 모양", objectName="section"))
        seg_box = QFrame()
        seg_box.setStyleSheet(f"QFrame {{ background:{BG}; border-radius:13px; }}")
        seg = QHBoxLayout(seg_box)
        seg.setContentsMargins(3, 3, 3, 3)
        seg.setSpacing(3)
        self.seg_group = QButtonGroup(self)
        self.segs = {}
        for key, name in [("glyph", "아이콘"), ("image", "내 이미지"), ("none", "글자만")]:
            sb = QPushButton(name, objectName="seg", checkable=True)
            self.seg_group.addButton(sb)
            sb.clicked.connect(lambda _=False, k=key: self._on_seg(k))
            seg.addWidget(sb)
            self.segs[key] = sb
        lay.addWidget(seg_box)

        # 아이콘 고르기 격자
        self.glyph_box = QWidget()
        gl = FlowLayout(self.glyph_box, spacing=4)       # 폭에 맞춰 줄바꿈
        gl.setContentsMargins(0, 4, 0, 0)
        self.glyph_group = QButtonGroup(self)
        self.glyph_btns = {}
        for i, (name, (ko, _)) in enumerate(GLYPHS.items()):
            if name == "plus":
                continue
            gb = QToolButton(objectName="glyph", checkable=True)
            gb.setFixedSize(40, 40)
            gb.setIcon(QIcon(QPixmap.fromImage(glyph_image(name, INK, 44))))
            gb.setIconSize(QSize(22, 22))
            gb.setToolTip(ko)
            gb.setCursor(Qt.PointingHandCursor)
            gb.clicked.connect(lambda _=False, n=name: self._pick_glyph(n))
            self.glyph_group.addButton(gb)
            gl.addWidget(gb)
            self.glyph_btns[name] = gb
        lay.addWidget(self.glyph_box)

        # 내 이미지
        self.image_box = QWidget(objectName="page")
        il = QHBoxLayout(self.image_box)
        il.setContentsMargins(0, 4, 0, 0)
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(64, 64)
        self.pick_image_btn = QPushButton("이미지 바꾸기")
        self.pick_image_btn.clicked.connect(self.pick_image)
        self.adjust_btn = QPushButton("위치 조정")
        self.adjust_btn.setToolTip("보관된 원본에서 보일 부분을 다시 골라")
        self.adjust_btn.clicked.connect(self.adjust_image)
        il.addWidget(self.image_preview, 0, Qt.AlignTop)
        il.addSpacing(4)
        img_btns = QWidget()
        ib = FlowLayout(img_btns, spacing=6)             # 좁으면 '위치 조정'이 아래 줄로
        ib.addWidget(self.pick_image_btn)
        ib.addWidget(self.adjust_btn)
        il.addWidget(img_btns, 1)
        lay.addWidget(self.image_box)

        lay.addSpacing(8)
        lay.addWidget(QLabel("바탕색", objectName="section"))
        sw_box = QWidget()
        sw = FlowLayout(sw_box, spacing=6)               # 폭에 맞춰 줄바꿈
        self.swatch_group = QButtonGroup(self)
        self.swatches = {}
        for col in SWATCHES:
            s = QPushButton(checkable=True)
            s.setFixedSize(30, 30)
            s.setCursor(Qt.PointingHandCursor)
            s.setStyleSheet(f"""
                QPushButton {{ background:{col}; border:1px solid {LINE}; border-radius:15px; padding:0; }}
                QPushButton:hover {{ border:2px solid {MINT}; }}
                QPushButton:checked {{ border:3px solid {MINT_D}; }}""")
            s.clicked.connect(lambda _=False, c=col: self._pick_color(c))
            self.swatch_group.addButton(s)
            sw.addWidget(s)
            self.swatches[col] = s
        more = QPushButton("직접", objectName="ghost")
        more.clicked.connect(self.custom_color)
        sw.addWidget(more)
        lay.addWidget(sw_box)

        card2 = QFrame(objectName="sub")
        lay = QVBoxLayout(card2)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)
        outer.addWidget(card2)
        lay.addWidget(QLabel("누르면 할 일", objectName="section"))
        self.type_combo = QComboBox()
        for key, name in ACTION_TYPES:
            self.type_combo.addItem(name, key)
        self.type_combo.currentIndexChanged.connect(self._on_type)
        lay.addWidget(self.type_combo)

        self.target_stack = QStackedWidget()
        p0 = QWidget(objectName="page")
        r0 = QHBoxLayout(p0)
        r0.setContentsMargins(0, 0, 0, 0)
        self.cmd_edit = QLineEdit()
        self.cmd_edit.textEdited.connect(lambda t: self._set("cmd", t))
        self.browse_btn = QPushButton("찾아보기")
        self.browse_btn.clicked.connect(self.browse)
        r0.addWidget(self.cmd_edit, 1)
        r0.addWidget(self.browse_btn)
        p1 = QWidget(objectName="page")
        r1 = QHBoxLayout(p1)
        r1.setContentsMargins(0, 0, 0, 0)
        self.key_edit = QKeySequenceEdit()
        if hasattr(self.key_edit, "setMaximumSequenceLength"):
            self.key_edit.setMaximumSequenceLength(1)
        self.key_edit.keySequenceChanged.connect(self._on_key)
        r1.addWidget(self.key_edit)
        # 그룹: 열 것 목록 (프로그램·파일·웹 주소), 순서 바꾸기, 사이 간격
        p2 = QWidget(objectName="page")
        g2 = QVBoxLayout(p2)
        g2.setContentsMargins(0, 0, 0, 0)
        g2.setSpacing(6)
        self.group_list = QListWidget(objectName="group")
        self.group_list.setMinimumHeight(118)
        self.group_list.setTextElideMode(Qt.ElideMiddle)
        self.group_list.currentRowChanged.connect(lambda _: self._update_group_buttons())
        g2.addWidget(self.group_list)
        add_row = QHBoxLayout()
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("경로나 https:// 주소를 넣고 Enter")
        self.group_input.returnPressed.connect(self._group_add_text)
        add_row.addWidget(self.group_input, 1)
        g_browse = QPushButton("찾아보기")
        g_browse.clicked.connect(self._group_browse)
        add_row.addWidget(g_browse)
        g2.addLayout(add_row)
        btn_box = QWidget()
        bl = FlowLayout(btn_box, spacing=6)
        self.group_up = QPushButton("↑ 위로", objectName="ghost")
        self.group_up.clicked.connect(lambda: self._group_move(-1))
        self.group_down = QPushButton("↓ 아래로", objectName="ghost")
        self.group_down.clicked.connect(lambda: self._group_move(1))
        self.group_del = QPushButton("빼기", objectName="ghost")
        self.group_del.clicked.connect(self._group_remove)
        for w in (self.group_up, self.group_down, self.group_del):
            bl.addWidget(w)
        g2.addWidget(btn_box)
        gap_row = QHBoxLayout()
        gap_row.addWidget(QLabel("하나 열고 다음까지", objectName="hint"))
        self.gap_spin = QDoubleSpinBox()
        self.gap_spin.setRange(0, 10)
        self.gap_spin.setSingleStep(0.5)
        self.gap_spin.setDecimals(1)
        self.gap_spin.setSuffix(" 초")
        self.gap_spin.valueChanged.connect(lambda v: self._set("gap", float(v), refresh_tile=False))
        gap_row.addWidget(self.gap_spin)
        gap_row.addStretch()
        g2.addLayout(gap_row)
        self.target_stack.addWidget(p0)
        self.target_stack.addWidget(p1)
        self.target_stack.addWidget(p2)
        lay.addWidget(self.target_stack)
        self.target_hint = QLabel(objectName="hint")
        self.target_hint.setWordWrap(True)
        lay.addWidget(self.target_hint)

        outer.addStretch()
        footer = QWidget(objectName="page")
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(18, 4, 18, 12)
        fl.setSpacing(8)
        pl.addWidget(footer)
        r2 = QHBoxLayout()
        self.left_btn = QPushButton("← 앞으로")
        self.left_btn.clicked.connect(lambda: self.move(-1))
        self.right_btn = QPushButton("뒤로 →")
        self.right_btn.clicked.connect(lambda: self.move(1))
        self.del_btn = QPushButton("삭제", objectName="danger")
        self.del_btn.clicked.connect(self.delete_button)
        r2.addWidget(self.left_btn)
        r2.addWidget(self.right_btn)
        r2.addStretch()
        r2.addWidget(self.del_btn)
        fl.addLayout(r2)
        self.test_btn = QPushButton("PC에서 테스트", objectName="primary")
        self.test_btn.setCursor(Qt.PointingHandCursor)
        self.test_btn.clicked.connect(self.test_action)
        fl.addWidget(self.test_btn)

        self.editor_widgets = [self.name_edit, seg_box, self.glyph_box, self.image_box, self.type_combo,
                               self.target_stack, self.left_btn, self.right_btn, self.del_btn, self.test_btn]
        self.editor_widgets += list(self.swatches.values()) + [more]
        return panel

    # ── 선택 / 편집 ──
    def select(self, bid):
        self.selected = bid
        for k, t in self.tiles.items():
            t.selected = k == bid
            t.update()
        b = self.store.get(bid) if bid else None
        if b:
            self.icon_view = "image" if self.store.image_path(b["icon"]) else ("glyph" if b["glyph"] else "none")
        self._load_editor()

    def _load_editor(self):
        b = self.store.get(self.selected) if self.selected else None
        for w in self.editor_widgets:
            w.setEnabled(b is not None)
        self.loading = True
        if b is None:
            self.name_edit.setText("")
            self.cmd_edit.setText("")
            self.target_hint.setText("왼쪽에서 버튼을 고르거나 '버튼 추가'를 눌러 줘")
            self.glyph_box.hide()
            self.image_box.hide()
        else:
            self.name_edit.setText(b["label"])
            self.hero_tile.set_button(b, self.store)
            self._refresh_hero_sub()
            self.segs[self.icon_view].setChecked(True)
            self.glyph_box.setVisible(self.icon_view == "glyph")
            self.image_box.setVisible(self.icon_view == "image")
            for n, gb in self.glyph_btns.items():
                gb.setChecked(n == b["glyph"] and self.icon_view == "glyph")
            p = self.store.image_path(b["icon"])
            if p:
                pm = QPixmap(p).scaled(64, 64, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                rounded = QPixmap(64, 64)
                rounded.fill(Qt.transparent)
                rp = QPainter(rounded)
                rp.setRenderHint(QPainter.Antialiasing)
                clip = QPainterPath()
                clip.addRoundedRect(0, 0, 64, 64, 14, 14)
                rp.setClipPath(clip)
                rp.drawPixmap(0, 0, pm)
                rp.end()
                self.image_preview.setPixmap(rounded)
            col = b["color"].lower()
            self.swatch_group.setExclusive(False)
            for c, s in self.swatches.items():
                s.setChecked(c == col)
            self.swatch_group.setExclusive(True)
            self.type_combo.setCurrentIndex([k for k, _ in ACTION_TYPES].index(b["type"]))
            self.cmd_edit.setText(b["cmd"] if b["type"] != "hotkey" else "")
            self.key_edit.setKeySequence(QKeySequence(b["cmd"]) if b["type"] == "hotkey" else QKeySequence())
            self._fill_group(b)
            self._update_target_ui(b["type"])
        self.loading = False

    def _update_target_ui(self, t):
        cur = {"hotkey": 1, "group": 2}.get(t, 0)
        self.target_stack.setCurrentIndex(cur)
        for i in range(self.target_stack.count()):     # 보이는 칸 높이만 차지하게 (그룹 칸 때문에 빈자리 안 생기게)
            self.target_stack.widget(i).setSizePolicy(
                QSizePolicy.Preferred, QSizePolicy.Preferred if i == cur else QSizePolicy.Ignored)
        self.target_stack.adjustSize()
        self.browse_btn.setVisible(t == "run")
        hints = {
            "run": "프로그램(.exe)이나 파일, 바로가기를 고르면 돼. 명령어를 직접 써도 돼.",
            "url": "예: https://www.youtube.com",
            "hotkey": "칸을 클릭하고 보낼 단축키를 그대로 눌러. OBS 단축키랑 맞추면 장면 전환에 쓸 수 있어. "
                      "받는 프로그램이 관리자 권한으로 켜져 있으면 TabDeck도 관리자 권한으로 켜야 해.",
            "group": "버튼 하나로 위에서부터 차례로 열어. 프로그램·파일·바로가기와 https:// 주소를 섞어도 돼. "
                     "한 번에 여러 개 고를 수도 있어.",
        }
        self.cmd_edit.setPlaceholderText("https://..." if t == "url" else "C:\\...\\program.exe")
        self.target_hint.setText(hints[t])

    def _set(self, field, value, refresh_tile=True):
        if self.loading or not self.selected:
            return
        self.store.update(self.selected, **{field: value})
        if refresh_tile and self.selected in self.tiles:
            self.tiles[self.selected].set_button(self.store.get(self.selected), self.store)
        self.save_timer.start()

    def _on_seg(self, key):
        b = self.store.get(self.selected)
        if key == "image":
            if not self.store.image_path(b["icon"]) and not self.pick_image():
                self._load_editor()          # 이미지 고르기를 취소하면 원래대로
                return
        elif key == "glyph":
            self._set("icon", "")
            if not b["glyph"]:
                self._set("glyph", "star")
        else:
            self._set("icon", "")
            self._set("glyph", "")
        self.icon_view = key
        self._load_editor()

    def _pick_glyph(self, name):
        self._set("icon", "")
        self._set("glyph", name)
        self.tiles[self.selected].play_result(True)

    def pick_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "버튼에 넣을 이미지 고르기", "",
                                              "이미지 (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.ico)")
        if not path:
            return False
        try:
            src = self.store.import_source(path, self.selected)
        except Exception as e:
            QMessageBox.warning(self, "TabDeck", str(e))
            return False
        if not self._crop(src, None):
            self.store.drop_file(SRC_DIR, src)     # 자르기를 취소하면 방금 복사한 원본도 정리
            return False
        return True

    def adjust_image(self):
        """'위치 조정': 보관된 원본에서 다시 자르기"""
        b = self.store.get(self.selected)
        src, note = b.get("src", ""), ""
        if not self.store.source_path(src):
            src = self.store.adopt_icon_as_source(self.selected)
            if not src:
                return
            self._set("src", src, refresh_tile=False)
            self._set("crop", None, refresh_tile=False)
            note = "예전에 넣은 이미지라 원본이 없어서, 지금 버튼 그림 안에서만 조정돼. 더 넓게 고르려면 '이미지 바꾸기'로 다시 넣어 줘."
        self._crop(src, self.store.get(self.selected).get("crop"), note)

    def _crop(self, src, crop, note=""):
        """자르기 창을 열고, 적용하면 버튼 이미지로 저장"""
        b = self.store.get(self.selected)
        img = self.store.read_image(self.store.source_path(src))
        if img is None:
            QMessageBox.warning(self, "TabDeck", "원본 이미지를 읽을 수 없어")
            return False
        dlg = CropDialog(self, img, b, crop, note)
        if dlg.exec() != QDialog.Accepted:
            return False
        crop = dlg.crop()
        name = self.store.save_crop(self.selected, img, crop)
        old_icon, old_src = b["icon"], b.get("src", "")
        self._set("src", src, refresh_tile=False)
        self._set("crop", crop, refresh_tile=False)
        self._set("icon", name)
        if old_icon != name:
            self.store.drop_file(ICON_DIR, old_icon)   # 이전에 잘라 둔 그림은 정리
        if old_src != src:
            self.store.drop_file(SRC_DIR, old_src)     # 이미지를 바꿨으면 예전 원본도 정리
        self.icon_view = "image"
        self._load_editor()
        return True

    def _pick_color(self, col):
        self._set("color", col)
        self._load_editor()

    def custom_color(self):
        b = self.store.get(self.selected)
        c = QColorDialog.getColor(QColor(b["color"]), self, "바탕색")
        if c.isValid():
            self._pick_color(c.name())

    def _on_type(self, i):
        if self.loading:
            return
        self._set("type", self.type_combo.itemData(i), refresh_tile=False)
        self._set("cmd", "", refresh_tile=False)
        self._load_editor()

    # ── 그룹 목록 편집 ──
    def _fill_group(self, b):
        self.group_list.clear()
        for item in b.get("group", []):
            self.group_list.addItem(self._group_label(item))
            self.group_list.item(self.group_list.count() - 1).setToolTip(item)
        self.gap_spin.setValue(float(b.get("gap", 0.5) or 0))
        self._update_group_buttons()

    @staticmethod
    def _group_label(item):
        if re.match(r"(?i)https?://", item):
            return "🌐  " + item
        return "▶  " + (os.path.basename(item.rstrip("\\/")) or item)

    def _group_items(self):
        return list(self.store.get(self.selected).get("group", [])) if self.selected else []

    def _group_save(self, items, row=None):
        self._set("group", items, refresh_tile=False)
        self._fill_group(self.store.get(self.selected))
        if row is not None and 0 <= row < self.group_list.count():
            self.group_list.setCurrentRow(row)
        self._refresh_hero_sub()

    def _update_group_buttons(self):
        row, n = self.group_list.currentRow(), self.group_list.count()
        self.group_up.setEnabled(row > 0)
        self.group_down.setEnabled(0 <= row < n - 1)
        self.group_del.setEnabled(row >= 0)

    def _group_add_text(self):
        text = self.group_input.text().strip().strip('"')
        if text:
            items = self._group_items() + [text]
            self.group_input.clear()
            self._group_save(items, len(items) - 1)

    def _group_browse(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "그룹에 넣을 프로그램·파일 고르기 (여러 개 가능)", "", "모든 파일 (*.*)")
        if paths:
            items = self._group_items() + [os.path.normpath(p) for p in paths]
            self._group_save(items, len(items) - 1)

    def _group_move(self, d):
        row, items = self.group_list.currentRow(), self._group_items()
        if 0 <= row < len(items) and 0 <= row + d < len(items):
            items[row], items[row + d] = items[row + d], items[row]
            self._group_save(items, row + d)

    def _group_remove(self):
        row, items = self.group_list.currentRow(), self._group_items()
        if 0 <= row < len(items):
            del items[row]
            self._group_save(items, min(row, len(items) - 1))

    def _refresh_hero_sub(self):
        b = self.store.get(self.selected) if self.selected else None
        if not b:
            return
        kind = dict(ACTION_TYPES)[b["type"]]
        if b["type"] == "group":
            n = len(b.get("group", []))
            self.hero_sub.setText(f"{kind} · {n}개" if n else kind)
        else:
            self.hero_sub.setText(f"{kind} · {b['cmd']}" if b["cmd"] else kind)

    def _on_key(self, seq):
        if self.loading:
            return
        text = seq.toString(QKeySequence.PortableText).split(",")[0].strip().lower()
        self._set("cmd", text, refresh_tile=False)

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "실행할 프로그램이나 파일 고르기", "", "모든 파일 (*.*)")
        if path:
            path = os.path.normpath(path)
            self.cmd_edit.setText(path)
            self._set("cmd", path, refresh_tile=False)

    def _save_and_push(self):
        self.store.save()
        self.store.rebuild()
        self.server.broadcast()

    def add_button(self):
        bid = self.store.add()
        self.refresh_grid()
        self.select(bid)
        self.save_timer.start()
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    def delete_button(self):
        b = self.store.get(self.selected)
        if QMessageBox.question(self, "TabDeck", f"'{b['label']}' 버튼을 지울까?") != QMessageBox.Yes:
            return
        self.store.remove(self.selected)
        self.store.drop_file(ICON_DIR, b["icon"])          # 이 버튼만 쓰던 이미지와 원본도 정리
        self.store.drop_file(SRC_DIR, b.get("src", ""))
        self.selected = None
        self.refresh_grid()
        self.select(self.store.buttons[0]["id"] if self.store.buttons else None)
        self.save_timer.start()

    def move(self, step):
        self.store.move(self.selected, step)
        self.refresh_grid()
        self.save_timer.start()

    # ── 테스트 버튼: 실행 중 → 체크 표시 ──
    def _set_test_state(self, state, text):
        self.test_btn.setProperty("state", state)
        self.test_btn.style().unpolish(self.test_btn)
        self.test_btn.style().polish(self.test_btn)
        self.test_btn.setText(text)

    def test_action(self):
        if self.testing:
            return
        b = self.store.get(self.selected)
        self.testing = True
        tile = self.tiles.get(self.selected)
        if b["type"] == "hotkey":
            self._set_test_state("busy", "1.5초 뒤에 단축키를 보낼게 · 원하는 창을 눌러 둬")
            delay = 1500
        else:
            self._set_test_state("busy", "실행 중 ·")
            dots = iter(["실행 중 · ·", "실행 중 · · ·"])
            for i, t in enumerate(dots):
                QTimer.singleShot(140 * (i + 1), lambda t=t: self.testing and self.test_btn.setText(t))
            delay = 420

        def go():
            # 실행은 따로 돌림: 그룹 실행은 간격만큼 기다리니까 창이 멈추지 않게
            def work():
                try:
                    run_action(dict(b))
                    self.test_finished.emit(True, f"테스트 실행 · {b['label']}")
                except Exception as e:
                    self.test_finished.emit(False, f"실패 · {e}")
            threading.Thread(target=work, daemon=True).start()

        def finish(ok, msg):
            self.log_label.setText(msg)
            if tile:
                tile.play_result(ok)
            self.sound.play("done" if ok else "fail")
            self._set_test_state("ok" if ok else "fail", "✓  실행됐어" if ok else "✕  실행 실패")
            QTimer.singleShot(1400, done)

        def done():
            self.testing = False
            self._set_test_state("", "PC에서 테스트")

        self._test_cb = finish
        QTimer.singleShot(delay, go)

    def _on_test_finished(self, ok, msg):
        # 창의 메서드로 받아야 다른 스레드에서 보낸 결과가 화면 스레드에서 처리됨
        cb, self._test_cb = getattr(self, "_test_cb", None), None
        if cb:
            cb(ok, msg)

    # ── 트레이 아이콘 ──
    def _build_tray(self):
        self.tray = QSystemTrayIcon(app_icon(), self)
        self.tray.setToolTip("TabDeck")
        menu = QMenu()
        open_act = QAction("설정 열기", self)
        open_act.triggered.connect(self.show_window)
        quit_act = QAction("종료", self)
        quit_act.triggered.connect(QApplication.instance().quit)
        menu.addAction(open_act)
        menu.addSeparator()
        menu.addAction(quit_act)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda r: self.show_window() if r in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick) else None)
        self.tray.show()

    def show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, e):
        # X를 눌러도 꺼지지 않고 트레이로 숨음 (완전히 끄려면 트레이 메뉴 → 종료)
        if self.save_timer.isActive():
            self.save_timer.stop()
            self._save_and_push()
        if QSystemTrayIcon.isSystemTrayAvailable():
            e.ignore()
            self.hide()
            if not self.tray_hint_shown:
                self.tray.showMessage("TabDeck", "트레이에서 계속 실행 중이야. 완전히 끄려면 아이콘 우클릭 → 종료",
                                      app_icon(), 3000)
                self.tray_hint_shown = True
        else:
            e.accept()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("TabDeck")
    app.setWindowIcon(app_icon())

    # 이미 켜져 있으면 그 창을 앞으로 불러오고 끝냄 (두 번 실행하면 포트가 겹치니까)
    pipe = "TabDeck-" + hashlib.sha1(os.path.expanduser("~").encode("utf-8")).hexdigest()[:12]
    probe = QLocalSocket()
    probe.connectToServer(pipe)
    if probe.waitForConnected(300):
        probe.write(b"show")
        probe.flush()
        probe.waitForBytesWritten(300)
        return
    QLocalServer.removeServer(pipe)         # 예전에 비정상 종료하며 남은 흔적 정리
    single = QLocalServer()
    single.listen(pipe)

    for f in ("Pretendard-Regular.otf", "Pretendard-Bold.otf"):          # fonts 폴더에 있으면 씀 (없으면 다른 글꼴로)
        for folder in (RES_DIR, APP_DIR):                                # exe 안에 묶인 것 → 프로그램 옆 순서
            p = os.path.join(folder, "fonts", f)
            if os.path.exists(p):
                QFontDatabase.addApplicationFont(p)
                break
    app.setStyleSheet(STYLE)
    os.makedirs(BASE_DIR, exist_ok=True)
    store = Store()
    bridge = Bridge()
    server = DeckServer(store, bridge)
    win = MainWindow(store, server, bridge)

    def on_second_launch():
        c = single.nextPendingConnection()
        if c is not None:
            c.disconnectFromServer()
        win.show_window()
    single.newConnection.connect(on_second_launch)

    win.show()
    server.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
