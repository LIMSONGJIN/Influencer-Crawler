# BlogCraft Pro - 시작 가이드 🚀

## 📌 프로젝트 구조

BlogCraft Pro는 완전한 SaaS 블로그 생성 플랫폼입니다.

```
BlogCraft Pro/
├── 🏠 메인 페이지 (Landing)
├── 🔐 로그인/회원가입
├── 📊 사용자 대시보드
├── ✍️ 블로그 작성 (Editor)
├── 🎛️ 관리자 페이지
└── 💳 요금제 페이지
```

## 🚀 실행 방법

### 1. 전체 서비스 맵 보기 (시작점)
```bash
# 브라우저에서 열기
index-saas.html
```
👉 **이 페이지에서 모든 페이지로 이동 가능합니다!**

### 2. 개별 페이지 직접 접근

#### 🔐 **로그인 페이지** (신규 생성 필요)
```html
saas-login.html (아직 미구현)
```

#### ✍️ **블로그 작성 페이지** (메인 기능)
```html
index.html
```
- AI 블로그 생성
- 이미지 업로드 (최대 10장)
- SEO 최적화
- SNS 변환

#### 📊 **사용자 대시보드**
```html
saas-dashboard.html
```
- 사용량 모니터링
- 통계 확인
- 구독 관리

#### 💳 **요금제 페이지**
```html
saas-pricing.html
```
- 3단계 요금제
- 기능 비교
- 구독 선택

#### 🎛️ **관리자 대시보드**
```html
admin-dashboard.html
```
- 전체 시스템 관리
- 사용자 관리
- 수익 분석

## 📝 사용 시나리오

### 신규 사용자 흐름:
1. `index-saas.html` → 서비스 소개 확인
2. `saas-pricing.html` → 요금제 선택
3. `saas-login.html` → 회원가입 (구현 필요)
4. `index.html` → 블로그 작성 시작
5. `saas-dashboard.html` → 사용량 확인

### 기존 사용자 흐름:
1. `saas-login.html` → 로그인
2. `saas-dashboard.html` → 대시보드
3. `index.html` → 새 콘텐츠 작성

### 관리자 흐름:
1. `admin-dashboard.html` → 관리자 로그인
2. 시스템 전체 모니터링 및 관리

## 🛠️ 기술 스택

### Frontend
- HTML5 + Tailwind CSS
- Vanilla JavaScript
- Chart.js (차트)
- Font Awesome (아이콘)

### Backend (구현 필요)
- Node.js / Python / PHP
- MySQL (database-schema.sql 제공)
- REST API

### AI Integration
- Claude API
- OpenAI GPT-4 API
- Google Gemini API

## 💾 데이터베이스 설정

```sql
# MySQL에서 실행
mysql -u root -p < database-schema.sql
```

### 주요 테이블:
- users (사용자)
- subscription_plans (요금제)
- blog_posts (블로그 글)
- sns_conversions (SNS 변환)
- payment_history (결제 내역)

## 🔧 설정 필요 항목

### 1. API 키 설정
- Claude API Key
- OpenAI API Key
- Google Gemini API Key

### 2. 결제 시스템
- Stripe / PayPal / 토스페이먼츠

### 3. 이메일 서비스
- SendGrid / AWS SES

## 📱 주요 기능

### 블로그 작성 (index.html)
✅ 플랫폼별 최적화 (네이버, 티스토리, 워드프레스)
✅ 이미지 업로드 및 자동 삽입
✅ SEO 분석 및 최적화
✅ SNS 자동 변환 (5개 플랫폼)
✅ HTML/MD 다운로드

### 사용자 대시보드
✅ 실시간 사용량 추적
✅ 주간/월간 통계
✅ 구독 관리
✅ 활동 기록

### 관리자 기능
✅ 사용자 관리
✅ 수익 분석
✅ 시스템 설정
✅ 활동 로그

## 🚦 다음 단계 (구현 필요)

1. **로그인/회원가입 페이지 생성**
   - `saas-login.html` 구현
   - JWT 인증
   - 소셜 로그인

2. **백엔드 API 개발**
   - 사용자 인증
   - 데이터 CRUD
   - 결제 처리

3. **실시간 연동**
   - WebSocket
   - 실시간 알림
   - 협업 기능

## 📞 지원

문제가 있으시면 아래 경로로 문의하세요:
- 이슈: GitHub Issues
- 이메일: support@blogcraftpro.com
- 문서: /docs

## 라이선스

© 2025 BlogCraft Pro. All rights reserved.