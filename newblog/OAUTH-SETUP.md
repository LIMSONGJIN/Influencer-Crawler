# BlogCraft Pro - OAuth 소셜 로그인 설정 가이드

## 📌 현재 상태

현재 로컬 개발 환경에서는 **데모 모드**로 작동합니다.
- 소셜 로그인 버튼 클릭 시 이메일 입력 프롬프트가 나타납니다.
- 실제 OAuth 인증 없이 테스트할 수 있습니다.

## 🔐 실제 OAuth 설정 방법

### 1. Google 로그인 설정

#### 1.1 Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" → "OAuth 동의 화면" 설정
4. "API 및 서비스" → "사용자 인증 정보" → "OAuth 2.0 클라이언트 ID" 생성

#### 1.2 OAuth 클라이언트 설정
```
애플리케이션 유형: 웹 애플리케이션
승인된 JavaScript 원본: 
  - http://localhost:3000 (개발)
  - https://yourdomain.com (운영)
승인된 리디렉션 URI:
  - http://localhost:3000/callback.html (개발)
  - https://yourdomain.com/callback.html (운영)
```

#### 1.3 코드 수정
`saas-login.html` 파일에서:
```javascript
// YOUR_GOOGLE_CLIENT_ID를 실제 Client ID로 변경
authUrl = 'https://accounts.google.com/o/oauth2/v2/auth?' +
    'client_id=123456789-abcdefg.apps.googleusercontent.com&' + // 실제 ID로 변경
```

### 2. 카카오 로그인 설정

#### 2.1 Kakao Developers 설정
1. [Kakao Developers](https://developers.kakao.com/) 접속
2. "내 애플리케이션" → "애플리케이션 추가하기"
3. 앱 생성 후 "앱 설정" → "플랫폼" → "Web 플랫폼 등록"

#### 2.2 플랫폼 설정
```
사이트 도메인:
  - http://localhost:3000 (개발)
  - https://yourdomain.com (운영)
Redirect URI:
  - http://localhost:3000/callback.html (개발)
  - https://yourdomain.com/callback.html (운영)
```

#### 2.3 코드 수정
`saas-login.html` 파일에서:
```javascript
// YOUR_KAKAO_REST_API_KEY를 실제 REST API 키로 변경
authUrl = 'https://kauth.kakao.com/oauth/authorize?' +
    'client_id=abcdef123456789&' + // 실제 REST API 키로 변경
```

### 3. 네이버 로그인 설정

#### 3.1 Naver Developers 설정
1. [Naver Developers](https://developers.naver.com/) 접속
2. "Application" → "애플리케이션 등록"
3. "API 설정" → "네아로(네이버 아이디로 로그인)" 선택

#### 3.2 애플리케이션 설정
```
서비스 URL: https://yourdomain.com
Callback URL: 
  - http://localhost:3000/callback.html (개발)
  - https://yourdomain.com/callback.html (운영)
```

#### 3.3 코드 수정
`saas-login.html` 파일에서:
```javascript
// YOUR_NAVER_CLIENT_ID를 실제 Client ID로 변경
authUrl = 'https://nid.naver.com/oauth2.0/authorize?' +
    'client_id=AbCdEfGhIjKlMnOp&' + // 실제 Client ID로 변경
```

## 🚀 백엔드 구현 필요 사항

### 1. 토큰 교환 엔드포인트
카카오와 네이버의 경우 authorization code를 access token으로 교환하는 백엔드 API가 필요합니다.

```javascript
// 예시: Node.js Express
app.post('/api/auth/kakao', async (req, res) => {
    const { code } = req.body;
    
    // Kakao 토큰 엔드포인트 호출
    const tokenResponse = await fetch('https://kauth.kakao.com/oauth/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            grant_type: 'authorization_code',
            client_id: process.env.KAKAO_REST_API_KEY,
            client_secret: process.env.KAKAO_CLIENT_SECRET,
            redirect_uri: process.env.REDIRECT_URI,
            code: code,
        }),
    });
    
    const tokenData = await tokenResponse.json();
    
    // 사용자 정보 조회
    const userResponse = await fetch('https://kapi.kakao.com/v2/user/me', {
        headers: {
            'Authorization': `Bearer ${tokenData.access_token}`,
        },
    });
    
    const userData = await userResponse.json();
    
    // 세션 생성 및 JWT 토큰 발급
    // ...
    
    res.json({ success: true, user: userData });
});
```

### 2. 사용자 정보 저장
OAuth로 받은 사용자 정보를 데이터베이스에 저장:

```sql
INSERT INTO users (email, name, provider, provider_id, profile_picture)
VALUES (?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE
    last_login = NOW(),
    name = VALUES(name),
    profile_picture = VALUES(profile_picture);
```

## 📝 테스트 방법

### 로컬 개발 환경 (현재)
1. `saas-login.html` 페이지 열기
2. 소셜 로그인 버튼 클릭
3. 프롬프트에 이메일 입력
4. 대시보드로 자동 이동 확인

### 실제 환경
1. OAuth 설정 완료 후 Client ID/Key 교체
2. 백엔드 API 구현
3. `callback.html`에서 실제 API 호출하도록 수정
4. HTTPS 환경에서 테스트

## 🔧 환경별 설정

### package.json 예시
```json
{
  "scripts": {
    "dev": "OAUTH_MODE=demo node server.js",
    "prod": "OAUTH_MODE=production node server.js"
  }
}
```

### 환경 변수 (.env)
```
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Kakao OAuth
KAKAO_REST_API_KEY=your_kakao_rest_api_key
KAKAO_CLIENT_SECRET=your_kakao_client_secret

# Naver OAuth
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# Redirect URI
REDIRECT_URI=http://localhost:3000/callback.html
```

## 🎯 체크리스트

- [ ] Google Cloud Console에서 OAuth 2.0 클라이언트 생성
- [ ] Kakao Developers에서 앱 생성 및 설정
- [ ] Naver Developers에서 애플리케이션 등록
- [ ] Client ID/Key를 코드에 적용
- [ ] 백엔드 토큰 교환 API 구현
- [ ] 사용자 정보 데이터베이스 연동
- [ ] HTTPS 인증서 설정 (운영 환경)
- [ ] 리디렉션 URI 등록 및 검증

## 💡 주의사항

1. **보안**: Client Secret은 절대 프론트엔드 코드에 포함하지 마세요.
2. **HTTPS**: 운영 환경에서는 반드시 HTTPS를 사용하세요.
3. **도메인**: 개발과 운영 도메인을 모두 OAuth 설정에 등록하세요.
4. **에러 처리**: 네트워크 오류, 사용자 거부 등 다양한 에러 상황을 처리하세요.
5. **세션 관리**: JWT 토큰 또는 세션 쿠키로 로그인 상태를 관리하세요.