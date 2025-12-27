# AI Anime Server

애니메이션 프레임 생성을 위한 FastAPI 기반 백엔드 서버입니다.

## 🚀 주요 기능

- **Kling AI 통합**: Image-to-Video 모델을 통한 프레임 보간(Interpolation)
- **프레임 관리**: 생성된 프레임의 추출, 저장 및 MP4 렌더링
- **RESTful API**: 프론트엔드와 통신을 위한 고성능 엔드포인트 제공

## 🛠️ 기술 스택

- **Framework**: FastAPI
- **Language**: Python 3.12+
- **Image Processing**: OpenCV, Pillow
- **Authentication**: JWT (Kling AI)
- **Settings**: Pydantic Settings

## 📁 프로젝트 구조

```text
server/
├── app/
│   ├── main.py          # 서버 진입점 및 라우팅
│   ├── services.py      # 비즈니스 로직 (비디오 생성, 렌더링)
│   └── animator.py      # Kling AI API 통신 모듈
├── config/
│   ├── settings.py      # Pydantic 설정 관리
│   └── .env             # 환경 변수 (API 키 등)
├── Dockerfile           # 서버 컨테이너 빌드 설정
└── requirements.txt     # 의존성 패키지 목록
```

## ⚡ 빠른 시작

### 1. 가상환경 구축 및 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`config/.env` 파일을 작성합니다 ( `config/.env.example` 참고).

```env
KLING_ACCESS_KEY=your_key
KLING_SECRET_KEY=your_secret
```

### 3. 서버 실행

```bash
uvicorn app.main:app --reload
```

## 📡 API 주요 엔드포인트

- `POST /generate-video`: 키 프레임 간 비디오 생성
- `POST /regenerate`: 특정 구간 재생성 (Revision)
- `POST /render-video`: 작업된 프레임들을 MP4로 렌더링

## 🐳 Docker 실행

```bash
docker build -t ai-anime-server .
docker run -p 8000:8000 --env-file config/.env ai-anime-server
```
