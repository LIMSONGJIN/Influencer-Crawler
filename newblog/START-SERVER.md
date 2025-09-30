# 🚀 BlogCraft Pro 로컬 서버 실행 가이드

## 📋 빠른 시작

### 방법 1: Python 사용 (권장) 🐍
```bash
# Python 3가 설치되어 있는 경우
python server.py

# 또는
python3 server.py
```

### 방법 2: Node.js 사용 🟢
```bash
# Node.js가 설치되어 있는 경우
node server.js
```

### 방법 3: VS Code Live Server 🎯
1. VS Code에서 프로젝트 폴더 열기
2. `index-saas.html` 파일 우클릭
3. "Open with Live Server" 선택

---

## 🌐 접속 주소

서버 시작 후 브라우저에서 접속:
- **http://localhost:8000**

자동으로 메인 페이지가 열립니다!

---

## 📱 주요 페이지 직접 접속

| 페이지 | URL | 설명 |
|--------|-----|------|
| 메인 홈 | http://localhost:8000/index-saas.html | 서비스 전체 소개 |
| 로그인 | http://localhost:8000/saas-login.html | 로그인/회원가입 |
| 블로그 작성 | http://localhost:8000/index.html | AI 블로그 작성 도구 |
| 대시보드 | http://localhost:8000/saas-dashboard.html | 사용자 대시보드 |
| 요금제 | http://localhost:8000/saas-pricing.html | 구독 플랜 |
| 관리자 | http://localhost:8000/admin-dashboard.html | 관리자 패널 |

---

## 🔧 설치 필요 사항

### Python 설치 확인
```bash
python --version
# 또는
python3 --version
```

Python이 없다면: https://www.python.org/downloads/

### Node.js 설치 확인
```bash
node --version
```

Node.js가 없다면: https://nodejs.org/

---

## ❓ 문제 해결

### "포트가 이미 사용 중" 오류
```bash
# Windows에서 포트 확인
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID [프로세스ID] /F
```

### 이미지가 표시되지 않을 때
1. 브라우저 캐시 삭제 (Ctrl + F5)
2. 개발자 도구 (F12) > Network 탭에서 오류 확인
3. Console 탭에서 JavaScript 오류 확인

### API 키 설정
1. 블로그 작성 페이지에서 ⚙️ 설정 클릭
2. API 키 입력:
   - Claude API Key
   - OpenAI API Key
   - Google Gemini API Key
3. 저장 클릭

---

## 🎯 이미지 업로드 테스트

1. **블로그 작성** 페이지 접속 (http://localhost:8000/index.html)
2. 주제 입력 (예: "맛집 추천")
3. **고급 설정** 클릭
4. **참고 이미지 추가** 섹션에서:
   - 이미지 파일 선택 (최대 10장)
   - 각 이미지에 설명 추가
5. **콘텐츠 생성** 클릭
6. 생성된 콘텐츠에서 이미지가 [이미지 1], [이미지 2] 위치에 자동 삽입됨 확인

---

## 💡 팁

- **Chrome/Edge 브라우저** 사용 권장
- 개발자 도구(F12)를 열어두면 디버깅 용이
- 로컬 스토리지에 API 키와 설정이 저장됨

---

## 🛑 서버 종료

터미널에서 **Ctrl + C** 입력

---

## 📞 지원

문제가 있으시면 GitHub Issues에 문의하세요!