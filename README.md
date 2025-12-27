# AI Anime Video Generator

Kling AI를 활용한 AI 애니메이션 비디오 생성 및 동화(In-betweening) 시스템

## 📋 프로젝트 개요

최근 애니메이션 산업은 높은 인건비와 촉박한 제작 일정으로 인한 퀄리티 저하 문제를 겪고 있습니다. 본 프로젝트는 이러한 문제를 해결하기 위해 **AI 기술을 활용하여 고품질의 애니메이션 중간 프레임을 자동으로 생성**하는 도구를 제공합니다.

- **핵심 가치:** Kling AI의 Image-to-Video 능력을 활용하여 두 개의 키 프레임 사이의 자연스러운 움직임을 생성함으로써 제작 비용과 시간을 혁신적으로 절감합니다.
- **주요 기능:** 키 프레임 간 비디오 생성, 특정 구간 재생성(Revision), 최종 프레임 렌더링 및 비디오 추출.

---

## 🛠️ 기술 스택

![tech_stack](C:\work\AI-anime\assets\tech_stack.png)

### Frontend

- **Framework:** React 19 (Vite)
- **Language:** TypeScript
- **State Management:** Hooks (useState, useEffect)
- **Styling:** CSS3 (Vanilla)
- **Features:** 프레임 멀티 셀렉트, 구간 재생성 프롬프트, 실시간 애니메이션 미리보기, ZIP/MP4 내보내기

### Backend

- **Framework:** FastAPI (Python 3.12)
- **Libraries:** OpenCV (프레임 처리), PyJWT (Kling AI 인증), Pydantic (데이터 검증)
- **API:** Kling AI API (Image-to-Video)
- **Architecture:** Service/Route 분리 구조

### Infrastructure & Deployment

- **Cloud:** **Oracle Cloud Infrastructure (OCI)**
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Web Server:** Nginx (Docker 내장)

---

## 📁 프로젝트 구조

```text
AI-anime/
├── client/              # React 프론트엔드 (Vite)
│   ├── src/
│   │   ├── components/  # 재사용 UI 컴포넌트
│   │   └── App.tsx      # 메인 로직 및 UI
│   └── Dockerfile       # 프론트엔드 빌드 설정
├── server/              # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py      # API 엔드포인트 정의
│   │   └── services.py  # 비즈니스 로직 (AI 통신, 이미지 처리)
│   ├── config/          # 설정 및 환경 변수 관리
│   └── Dockerfile       # 백엔드 실행 설정
├── docker-compose.yml   # 전체 시스템 오케스트레이션
└── .github/workflows/   # CI/CD 자동화 (main.yml)
```

---

## 🚀 시작하기 (Local)

### 1. 환경 변수 설정

`server/config/.env` (또는 루트의 `.env`) 파일을 생성합니다:

```env
KLING_ACCESS_KEY=your_access_key
KLING_SECRET_KEY=your_secret_key
```

### 2. Docker Compose로 실행

이 방법이 가장 간단하며 모든 의존성을 포함합니다.

```bash
docker-compose up --build
```

- **Frontend:** http://localhost (80 포트)
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🌐 배포 및 CI/CD

### Oracle Cloud (OCI) 배포

본 프로젝트는 **Oracle Cloud** 인스턴스에 배포되어 있습니다.

- **환경:** Ubuntu 기반 VM, Docker Engine 설치
- **방식:** Docker Compose를 이용한 컨테이너 기반 배포

### GitHub Actions (CI/CD)

`.github/workflows/main.yml`을 통해 자동 배포가 이루어집니다:

1.  **Build & Push:** 코드가 `main` 브랜치에 푸시되면 Docker 이미지를 빌드하고 Docker Hub에 업로드합니다.
2.  **Deploy:** SSH를 통해 Oracle Cloud 인스턴스에 접속하여 최신 이미지를 `pull` 받고 `docker-compose up`을 통해 서비스를 갱신합니다.

---

## 🔑 주요 API 기능

- `POST /generate-video`: 시작/끝 이미지와 프롬프트를 통해 비디오 생성
- `POST /regenerate`: 특정 구간(프레임 범위)만 다른 프롬프트로 재생성
- `POST /render-video`: 작업된 모든 프레임을 하나의 MP4 비디오로 병합

---

## 📝 라이선스

본 프로젝트는 AI 기술을 활용한 애니메이션 제작 효율화 연구를 목적으로 하는 개인 프로젝트입니다.
