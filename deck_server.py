# deck_server.py — 안드로이드 스트림 덱용 PC 프로그램
import asyncio, json, os, secrets, socket, subprocess, webbrowser
import websockets

WS_PORT = 8765         # 앱과 연결되는 포트
DISCOVERY_PORT = 8766  # PC 자동 찾기 신호용 포트
CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck_config.json")

DEFAULT = {
    "key": secrets.token_urlsafe(6),
    "buttons": [
        {"id": "notepad", "label": "메모장", "type": "run", "cmd": "notepad.exe"},
        {"id": "calc",    "label": "계산기", "type": "run", "cmd": "calc.exe"},
        {"id": "yt",      "label": "유튜브", "type": "url", "cmd": "https://www.youtube.com"}
    ]
}

def load_config():
    if not os.path.exists(CONFIG):
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump(DEFAULT, f, ensure_ascii=False, indent=2)
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)

def run_action(b):
    if b["type"] == "run":
        subprocess.Popen(b["cmd"], shell=True)
    elif b["type"] == "url":
        webbrowser.open(b["cmd"])
    else:
        raise ValueError("모르는 type: " + b["type"])

async def handle(ws):
    cfg = load_config()                      # 접속할 때마다 설정을 새로 읽음
    try:
        hello = json.loads(await asyncio.wait_for(ws.recv(), 5))
        if hello.get("type") != "hello" or hello.get("key") != cfg["key"]:
            await ws.send(json.dumps({"type": "error", "msg": "비밀 키가 틀렸어"}, ensure_ascii=False))
            return
        await ws.send(json.dumps({"type": "buttons", "items": cfg["buttons"]}, ensure_ascii=False))
        print("기기 연결됨:", ws.remote_address[0])
        async for raw in ws:
            msg = json.loads(raw)
            if msg.get("type") != "press":
                continue
            b = next((x for x in cfg["buttons"] if x["id"] == msg.get("id")), None)
            ok = False
            if b:
                try:
                    run_action(b); ok = True; print("실행:", b["label"])
                except Exception as e:
                    print("오류:", e)
            await ws.send(json.dumps({"type": "result", "id": msg.get("id"), "ok": ok}))
    except Exception as e:
        print("연결 끊김:", e)

def local_ips():
    # PC에 연결된 모든 네트워크(랜선, Wi-Fi)의 IP를 찾음
    ips = {i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)}
    return [ip for ip in ips if not ip.startswith("127.")]

async def announce():
    # 2초마다 랜선, Wi-Fi 각각으로 "DECK:포트" 신호를 보냄
    msg = f"DECK:{WS_PORT}".encode()
    while True:
        for ip in local_ips():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.bind((ip, 0))   # 이 네트워크 쪽으로 보내라고 지정
                s.sendto(msg, (ip.rsplit(".", 1)[0] + ".255", DISCOVERY_PORT))
                s.close()
            except OSError:
                pass
        await asyncio.sleep(2)

async def main():
    print("비밀 키 (앱에 처음 한 번 입력):", load_config()["key"])
    async with websockets.serve(handle, "0.0.0.0", WS_PORT, ping_interval=10):
        await announce()

asyncio.run(main())