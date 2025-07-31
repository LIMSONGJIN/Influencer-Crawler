# Influencer-Crawler

TikTok, Instagram, Shein 등에서 데이터를 수집하는 크롤러 프로젝트입니다.

---

## 📦 환경 세팅

본 프로젝트는 Anaconda 환경을 사용합니다.

### 1. Conda 환경 생성 (Python 3.10.18 버전)

아래 명령어로 환경을 생성하세요.

```bash
conda env create -f environment.yml
```

### 2. 환경 활성화

생성한 conda 환경을 아래 명령어로 활성화합니다.

```bash
conda activate douyin-crawler
```

### 3. 패키지 추가/변경 시 환경 업데이트

`environment.yml`이 변경된 경우, 아래 명령어로 환경을 업데이트하세요.

```bash
conda env update -f environment.yml --prune
```

### 4. 환경 삭제 (원할 경우)

환경을 완전히 삭제하려면 아래 명령어를 사용하세요.

```bash
conda env remove -n douyin-crawler
```

---

## 🚀 실행 방법

1. 환경을 활성화한 상태에서 원하는 크롤러 폴더로 이동합니다.
2. 예시:
    ```bash
    cd TikTok
    python main.py
    ```

---

## 📄 참고

-   `environment.yml` 파일에 설치 패키지와 Python 버전이 정의되어 있습니다.
-   환경 이름(`douyin-crawler`)이 다를 경우, `environment.yml`에서 `name:` 부분을 원하는 이름으로 수정할 수 있습니다.
-   추가적인 라이브러리가 필요하다면 `environment.yml`에 패키지를 추가한 뒤 환경을 업데이트하세요.

---

## 🔗 기타

기타 문의 및 기능 요청은 [Issues](https://github.com/LIMSONGJIN/Influencer-Crawler/issues)에 남겨주세요.
