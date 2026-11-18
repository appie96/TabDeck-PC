# TabDeck PC

남는 안드로이드 폰·태블릿을 스트림 덱처럼 쓰게 해 주는 TabDeck의 **PC 프로그램**이야.
같은 Wi-Fi의 TabDeck 앱이 버튼을 누르면, 이 프로그램이 PC에서 프로그램 실행·웹페이지 열기·단축키를 대신 실행해.

## 쓰는 법
1. [Releases](../../releases/latest)에서 `TabDeck.exe`를 받아서 실행해.
2. 처음 실행할 때 Windows 방화벽 창이 뜨면 **개인 네트워크**만 허용해 줘.
3. 폰·태블릿의 TabDeck 앱에 PC 화면에 보이는 **비밀 키**를 넣으면 연결돼.

설정과 버튼 이미지는 `%APPDATA%\TabDeck`에 저장돼. exe 옆에 `deck_config.json`이 있으면 그 폴더를 대신 써(휴대용).

## 직접 실행·빌드
```
pip install PySide6-Essentials websockets pynput
python deck_app.py
```
exe 만들기:
```
python -m pip install pyinstaller
python build_exe.py      # → dist\TabDeck.exe
```

## 보안
- 앱과 PC는 비밀 키로 서로 확인해 (HMAC-SHA256, 키 자체는 네트워크로 보내지 않음).
- 비밀 키는 PC 프로그램의 새로고침 버튼으로 언제든 새로 만들 수 있어.

## 사용한 것
- 아이콘: [Lucide](https://lucide.dev) (ISC 라이선스)
- 글꼴: [Pretendard](https://github.com/orioncactus/pretendard) (SIL Open Font License 1.1, `fonts/Pretendard-LICENSE.txt`)

## 라이선스
MIT 라이선스 (`LICENSE`). 아이콘과 글꼴은 위에 적은 각자의 라이선스를 따라.
