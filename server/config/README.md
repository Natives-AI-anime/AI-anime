# Settings Configuration Guide

## 📋 개요

이 프로젝트는 **Pydantic BaseModel**을 사용한 현대적인 설정 관리 시스템을 사용합니다.

## 🚀 빠른 시작

### 1. 환경 변수 파일 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env
```

### 2. API 키 설정

`.env` 파일을 열어 필요한 API 키를 입력하세요:

````bash
# Kling AI API 키 (필수)
KLING_ACCESS_KEY=your_actual_access_key
KLING_SECRET_KEY=your_actual_secret_key

### 3. 설정 사용하기

```python
from config.settings import settings

# 설정 값 사용
print(f"프로젝트명: {settings.PROJECT_NAME}")
print(f"서버 URL: {settings.get_api_url()}")
print(f"환경: {settings.ENVIRONMENT}")

# Kling AI API 키 사용
access_key = settings.KLING_ACCESS_KEY
secret_key = settings.KLING_SECRET_KEY
````

## 🔧 주요 설정 항목

### 환경 설정

| 변수명        | 기본값        | 설명                                       |
| ------------- | ------------- | ------------------------------------------ |
| `ENVIRONMENT` | `development` | 실행 환경 (development/staging/production) |
| `DEBUG`       | `True`        | 디버그 모드 활성화 여부                    |

### 서버 설정

| 변수명 | 기본값    | 설명             |
| ------ | --------- | ---------------- |
| `HOST` | `0.0.0.0` | 서버 호스트 주소 |
| `PORT` | `8000`    | 서버 포트 번호   |

### CORS 설정

| 변수명         | 기본값                                        | 설명                           |
| -------------- | --------------------------------------------- | ------------------------------ |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | CORS 허용 오리진 (쉼표로 구분) |

### API 키 설정

#### Kling AI

- `KLING_ACCESS_KEY`: Kling AI Access Key
- `KLING_SECRET_KEY`: Kling AI Secret Key
- `KLING_API_BASE_URL`: API 베이스 URL (기본: `https://api.klingai.com`)

### 파일 업로드 설정

| 변수명            | 기본값            | 설명                           |
| ----------------- | ----------------- | ------------------------------ |
| `MAX_UPLOAD_SIZE` | `10485760` (10MB) | 최대 업로드 파일 크기 (바이트) |
| `UPLOAD_DIR`      | `./uploads`       | 업로드 파일 저장 디렉토리      |

### 로깅 설정

| 변수명      | 기본값 | 설명                                          |
| ----------- | ------ | --------------------------------------------- |
| `LOG_LEVEL` | `INFO` | 로그 레벨 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `LOG_FILE`  | `None` | 로그 파일 경로 (비워두면 콘솔만 출력)         |

## 💡 고급 기능

### 환경별 설정

프로덕션 환경에서는 `.env` 파일의 `ENVIRONMENT` 값을 변경하세요:

```bash
# 프로덕션 환경
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
```

### 유틸리티 메서드

```python
from config.settings import settings

# 환경 확인
if settings.is_production():
    print("프로덕션 환경입니다")

if settings.is_development():
    print("개발 환경입니다")

# API URL 가져오기
api_url = settings.get_api_url()  # http://0.0.0.0:8000
```

### 타입 안정성

Pydantic을 사용하므로 타입이 자동으로 검증됩니다:

```python
# 자동으로 int로 변환됨
port = settings.PORT  # int 타입 보장

# 자동으로 bool로 변환됨
debug = settings.DEBUG  # bool 타입 보장

# 자동으로 List[str]로 변환됨
origins = settings.CORS_ORIGINS  # List[str] 타입 보장
```

### 검증 기능

설정 값이 유효하지 않으면 자동으로 에러가 발생합니다:

```bash
# 잘못된 환경 설정
ENVIRONMENT=invalid  # ❌ ValueError 발생

# 잘못된 로그 레벨
LOG_LEVEL=INVALID  # ❌ ValueError 발생
```

## 🔒 보안 주의사항

1. **절대로 `.env` 파일을 Git에 커밋하지 마세요!**

   - `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

2. **API 키는 안전하게 보관하세요**

   - 프로덕션 환경에서는 환경 변수나 시크릿 관리 서비스를 사용하세요

3. **`.env.example` 파일만 커밋하세요**
   - 실제 API 키 대신 플레이스홀더를 사용하세요

## 📚 참고 자료

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [FastAPI Settings Management](https://fastapi.tiangolo.com/advanced/settings/)

## 🐛 문제 해결

### 설정이 로드되지 않는 경우

1. `.env` 파일이 `config/` 디렉토리에 있는지 확인
2. 파일 인코딩이 UTF-8인지 확인
3. 환경 변수 이름이 정확한지 확인

### API 키 경고가 표시되는 경우

```
⚠️  경고: KLING_ACCESS_KEY이(가) 설정되지 않았습니다.
```

이는 해당 API 키가 `.env` 파일에 설정되지 않았음을 의미합니다. 필요한 경우 `.env` 파일에 키를 추가하세요.
