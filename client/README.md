# AI Anime Client

애니메이션 키 프레임을 기반으로 영상을 생성하고 편집하는 React 프론트엔드입니다.

## 🚀 주요 기능

- **Step-by-Step 워크플로우**:
  1.  **Creation**: 시작/끝 이미지 업로드 및 생성 프롬프트 입력
  2.  **Review**: 생성된 프레임 확인, 멀티 셀렉트 기능을 이용한 특정 구간 재생성(Revision)
  3.  **Export**: 최종 작업 결과물을 MP4 비디오 또는 ZIP(이미지 시퀀스) 파일로 내보내기
- **실시간 미리보기**: 생성된 프레임 애니메이션을 즉시 재생하며 속도 조절 가능
- **반응형 UI**: 다양한 모바일/데스크탑 환경 최적화

## 🛠️ 기술 스택

- **Framework**: React 19
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Vanilla CSS
- **Libraries**:
  - `jszip`: 이미지 시퀀스 압축 및 다운로드
  - `file-saver`: 파일 저장 유틸리티

## 📁 프로젝트 구조

```text
client/
├── src/
│   ├── components/
│   │   ├── studio/          # 단계별 작업 컴포넌트
│   │   │   ├── CreationStep.tsx
│   │   │   ├── ReviewStep.tsx
│   │   │   └── ExportStep.tsx
│   │   └── AnimeStudio.tsx  # 메인 스튜디오 컨테이너
│   ├── App.tsx              # 앱 레이아웃 및 라우팅
│   └── main.tsx             # 진입점
├── public/                  # 정적 자산
├── Dockerfile               # Nginx 기반 배포 설정
└── package.json             # 의존성 및 스크립트
```

## ⚡ 개발 시작

### 1. 의존성 설치

```bash
npm install
```

### 2. 로컬 실행

```bash
npm run dev
```

기본적으로 `http://localhost:5173`에서 실행됩니다.

## 🐳 Docker 배포

클라이언트는 Nginx를 통해 빌드된 정적 파일을 서빙합니다.

```bash
docker build -t ai-anime-client .
docker run -p 80:80 ai-anime-client
```

## 📡 백엔드 연결 설정

기본적으로 같은 호스트의 `8000` 포트를 바라보도록 설정되어 있습니다. (개발 환경에 따라 수동 조절 가능)
