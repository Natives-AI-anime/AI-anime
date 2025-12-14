# AI Anime Video Generator

Kling AI를 활용한 AI 애니메이션 비디오 생성 시스템

## 📋 프로젝트 개요

만화 컷(시작 프레임, 끝 프레임)을 입력하면 AI가 자동으로 부드러운 애니메이션을 생성해주는 프로젝트입니다.

## 🛠️ 기술 스택

### Backend

- **언어**: Python 3.x
- **웹 프레임워크**: FastAPI
- **ASGI 서버**: Uvicorn

### Core Libraries

- **opencv-python (cv2)**: 비디오 프레임 추출 및 처리
- **PyJWT**: JWT 토큰 생성 (Kling AI 인증)
- **requests**: HTTP API 통신
- **python-dotenv**: 환경 변수 관리
- **pydantic**: 데이터 검증 및 설정 관리

### External API

- **Kling AI API**: 이미지 기반 비디오 생성 (Image-to-Video)

### Development Tools

- **Git**: 버전 관리
- **venv**: Python 가상환경

## 📁 프로젝트 구조

```
AI-anime/
├── server/              # 백엔드 서버
│   ├── app/
│   │   ├── animator.py  # Kling AI 통신 및 비디오 생성
│   │   └── main.py      # FastAPI 애플리케이션
│   ├── config/
│   │   ├── settings.py  # 설정 관리
│   │   ├── .env         # 환경 변수 (API 키)
│   │   └── .env.example # 환경 변수 템플릿
│   ├── test_video_generation.py  # GUI 테스트 스크립트
│   ├── requirements.txt # Python 패키지 목록
│   └── .venv/          # 가상환경
├── client/             # 프론트엔드 (예정)
└── README.md
```

## 🚀 시작하기

### 1. 환경 설정

```bash
cd server
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. API 키 설정

`server/config/.env` 파일을 생성하고 Kling AI API 키를 입력하세요:

```env
KLING_ACCESS_KEY=your_access_key
KLING_SECRET_KEY=your_secret_key
```

### 3. 실행

#### GUI 테스트

```bash
python test_video_generation.py
```

#### API 서버

```bash
uvicorn app.main:app --reload
```

## 📡 API 엔드포인트

### `POST /generate-video`

비디오 생성 (시작/끝 이미지 → 애니메이션)

**요청**:

- `start_image`: 시작 프레임 (파일)
- `end_image`: 끝 프레임 (파일)
- `prompt`: 비디오 생성 프롬프트 (텍스트)
- `project_name`: 프로젝트 이름 (텍스트)

**응답**:

```json
{
  "status": "success",
  "message": "비디오 생성 완료",
  "data": {
    "project_name": "my_project",
    "frame_count": 150,
    "frames": ["path/to/frame1.jpg", ...]
  }
}
```

### `POST /regenerate-segment`

특정 구간 재생성 (Revision)

**요청** (JSON):

```json
{
  "project_name": "my_project",
  "start_image_path": "path/to/frame_10.jpg",
  "end_image_path": "path/to/frame_20.jpg",
  "target_frame_count": 11,
  "prompt": "smooth animation"
}
```

### `POST /generate-frame`

단일 프레임 생성 (말풍선 제거 등)

## 🔑 주요 기능

- ✅ 두 이미지 사이의 부드러운 애니메이션 생성
- ✅ 특정 구간 재생성 (Revision)
- ✅ 프레임 추출 및 저장
- ✅ GUI 기반 테스트 인터페이스
- ✅ RESTful API 제공

## 📝 라이선스

이 프로젝트는 개인 프로젝트입니다.
