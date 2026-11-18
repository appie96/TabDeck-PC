# TabDeck PC 프로그램을 exe 하나로 묶는 스크립트
#   준비(한 번만): python -m pip install pyinstaller
#   실행:          python build_exe.py
#   결과:          dist\TabDeck.exe  (이 파일 하나만 나눠 주면 됨)
import os, re, struct, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "build", "assets")
os.makedirs(ASSETS, exist_ok=True)

src = open(os.path.join(HERE, "deck_app.py"), encoding="utf-8").read()
VERSION = re.search(r'^VERSION = "([\d.]+)"', src, re.M).group(1)


def make_icon(path):
    """앱 아이콘을 여러 크기로 그려서 .ico 하나에 담음 (윈도우 탐색기·작업 표시줄용)"""
    sys.path.insert(0, HERE)
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QGuiApplication
    app = QGuiApplication.instance() or QGuiApplication([])
    import deck_app
    pngs = []
    for size in (16, 24, 32, 48, 64, 128, 256):
        buf = QBuffer()
        buf.open(QIODevice.WriteOnly)
        deck_app.app_icon_pixmap(size).save(buf, "PNG")
        pngs.append((size, bytes(buf.data())))
    head = struct.pack("<HHH", 0, 1, len(pngs))
    entries, body, offset = b"", b"", 6 + 16 * len(pngs)
    for size, data in pngs:
        s = 0 if size >= 256 else size            # .ico 규칙: 256은 0으로 적음
        entries += struct.pack("<BBBBHHII", s, s, 0, 0, 1, 32, len(data), offset)
        body += data
        offset += len(data)
    with open(path, "wb") as f:
        f.write(head + entries + body)


def make_version_file(path):
    """exe 파일 속성 → 자세히 탭에 보이는 정보"""
    v = tuple(int(x) for x in VERSION.split(".")) + (0,) * (4 - len(VERSION.split(".")))
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={v}, prodvers={v}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('041204B0', [
      StringStruct('FileDescription', 'TabDeck - 안드로이드 기기를 스트림 덱처럼'),
      StringStruct('ProductName', 'TabDeck'),
      StringStruct('FileVersion', '{VERSION}'),
      StringStruct('ProductVersion', '{VERSION}'),
      StringStruct('OriginalFilename', 'TabDeck.exe'),
      StringStruct('LegalCopyright', 'Icons: Lucide (ISC), Font: Pretendard (OFL)')])]),
    VarFileInfo([VarStruct('Translation', [0x0412, 1200])])
  ]
)
""")


icon = os.path.join(ASSETS, "tabdeck.ico")
version_file = os.path.join(ASSETS, "version.txt")
make_icon(icon)
make_version_file(version_file)

fonts = os.path.join(HERE, "fonts")
args = [
    sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
    "--onefile",                 # exe 하나로
    "--windowed",                # 검은 콘솔 창 없이
    "--name", "TabDeck",
    "--icon", icon,
    "--version-file", version_file,
    "--distpath", os.path.join(HERE, "dist"),
    "--workpath", os.path.join(HERE, "build", "work"),
    "--specpath", os.path.join(HERE, "build"),
    "--exclude-module", "tkinter",
]
for name in ("Pretendard-Regular.otf", "Pretendard-Bold.otf", "Pretendard-LICENSE.txt"):
    p = os.path.join(fonts, name)
    if os.path.exists(p):
        args += ["--add-data", f"{p}{os.pathsep}fonts"]
    else:
        print(f"[알림] {name} 없음 → 글꼴 없이 묶음 (맑은 고딕 등으로 보임)")
args.append(os.path.join(HERE, "deck_app.py"))

print(f"TabDeck {VERSION} 빌드 시작...")
subprocess.run(args, check=True, cwd=HERE)
exe = os.path.join(HERE, "dist", "TabDeck.exe")
print(f"\n완료: {exe} ({os.path.getsize(exe) / 1024 / 1024:.1f} MB)")
