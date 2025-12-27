# Configuration Guide

이 디렉토리는 **Pydantic Settings**를 활용한 프로젝트 설정 관리 시스템을 포함하고 있습니다.

## 🚀 설정 방법

### 1. 환경 변수 파일 (.env)

`server/config/.env` 파일을 생성하고 아래 내용을 설정합니다:

```env
# Kling AI API 키 (필수)
KLING_ACCESS_KEY=your_access_key
KLING_SECRET_KEY=your_secret_key

# 서버 설정
ENVIRONMENT=development
DEBUG=True
PORT=8000
```

### 2. 설정 사용법

코드 내에서 `settings` 객체를 통해 타입 안정성이 보장된 설정값을 가져올 수 있습니다.

```python
from config.settings import settings

# 설정 값 접근
print(settings.PROJECT_NAME)
print(settings.KLING_API_BASE_URL)

# 환경 판별 유틸리티
if settings.is_production():
    # 운영 환경 로직
    pass
```

## 🔧 주요 설정 변수

| 변수명            | 기본값        | 설명                                         |
| :---------------- | :------------ | :------------------------------------------- |
| `ENVIRONMENT`     | `development` | 실행 환경 (development, staging, production) |
| `DEBUG`           | `True`        | 디버그 모드 활성 여부                        |
| `PORT`            | `8000`        | 서버 포트 번호                               |
| `MAX_UPLOAD_SIZE` | `10MB`        | 최대 업로드 허용 크기                        |
| `LOG_LEVEL`       | `INFO`        | 로깅 레벨 (DEBUG, INFO, ...)                 |

## 🔒 보안 주의사항

1. **`.env` 파일은 절대 Git에 포함하지 마세요.** (이미 `.gitignore`에 등록되어 있습니다)
2. **`.env.example`** 파일을 통해 팀원들에게 필요한 설정 항목을 공유하세요.
3. API 키와 같은 민감 정보는 운영 환경에서 환경 변수로 관리할 것을 권장합니다.

## 📚 참고

- [Pydantic Settings Docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
