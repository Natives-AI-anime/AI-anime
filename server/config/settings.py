# -----------------------------------------------------------------------------
# config/settings.py
# -----------------------------------------------------------------------------
"""
프로젝트 설정 관리 모듈

이 파일은 프로젝트의 모든 설정을 중앙에서 관리합니다.
Pydantic을 사용하여 타입 안정성과 자동 검증을 제공합니다.
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# .env 파일 경로 설정 및 로드
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH, encoding='utf-8')


class Settings(BaseModel):
    """
    애플리케이션 설정 클래스
    
    Pydantic BaseModel을 상속받아 타입 검증과 자동 변환을 지원합니다.
    환경 변수에서 값을 읽어오며, 기본값을 제공합니다.
    """
    
    # =========================================================================
    # 프로젝트 기본 정보
    # =========================================================================
    PROJECT_NAME: str = "AI Anime Generator"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI 기반 애니메이션 프레임 생성 서비스"
    
    # =========================================================================
    # 환경 설정
    # =========================================================================
    ENVIRONMENT: str = Field(
        default=os.getenv("ENVIRONMENT", "development"),
        description="실행 환경 (development, staging, production)"
    )
    DEBUG: bool = Field(
        default=os.getenv("DEBUG", "True").lower() == "true",
        description="디버그 모드 활성화 여부"
    )
    
    # =========================================================================
    # 서버 설정
    # =========================================================================
    HOST: str = Field(
        default=os.getenv("HOST", "0.0.0.0"),
        description="서버 호스트 주소"
    )
    PORT: int = Field(
        default=int(os.getenv("PORT", "8000")),
        description="서버 포트 번호"
    )
    
    # =========================================================================
    # CORS 설정
    # =========================================================================
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:3000,http://localhost:8000"
        ).split(","),
        description="CORS 허용 오리진 목록"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    
    # =========================================================================
    # Kling AI API 설정
    # =========================================================================
    KLING_ACCESS_KEY: str = Field(
        default=os.getenv("KLING_ACCESS_KEY", ""),
        description="Kling AI Access Key"
    )
    KLING_SECRET_KEY: str = Field(
        default=os.getenv("KLING_SECRET_KEY", ""),
        description="Kling AI Secret Key"
    )
    KLING_API_BASE_URL: str = Field(
        default=os.getenv("KLING_API_BASE_URL", "https://api.klingai.com"),
        description="Kling AI API 베이스 URL"
    )
    
    # =========================================================================
    # 파일 업로드 설정
    # =========================================================================
    MAX_UPLOAD_SIZE: int = Field(
        default=int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024))),  # 10MB
        description="최대 업로드 파일 크기 (바이트)"
    )
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".webp", ".gif"],
        description="허용되는 이미지 확장자"
    )
    UPLOAD_DIR: Path = Field(
        default=Path(os.getenv("UPLOAD_DIR", "./uploads")),
        description="업로드 파일 저장 디렉토리"
    )
    
    # =========================================================================
    # 로깅 설정
    # =========================================================================
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    LOG_FILE: Optional[str] = Field(
        default=os.getenv("LOG_FILE", None),
        description="로그 파일 경로 (None이면 콘솔만 출력)"
    )
    
    # =========================================================================
    # 데이터베이스 설정 (필요시 활성화)
    # =========================================================================
    # DATABASE_URL: str = Field(
    #     default=os.getenv("DATABASE_URL", "sqlite:///./app.db"),
    #     description="데이터베이스 연결 URL"
    # )
    
    # =========================================================================
    # Redis 설정 (캐싱용, 필요시 활성화)
    # =========================================================================
    # REDIS_URL: str = Field(
    #     default=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    #     description="Redis 연결 URL"
    # )
    
    # =========================================================================
    # 검증 메서드
    # =========================================================================
    @field_validator("KLING_ACCESS_KEY", "KLING_SECRET_KEY")
    @classmethod
    def validate_kling_keys(cls, v: str, info) -> str:
        """Kling AI API 키 검증"""
        if not v:
            print(f"⚠️  경고: {info.field_name}이(가) 설정되지 않았습니다.")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """로그 레벨 검증"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL은 {valid_levels} 중 하나여야 합니다.")
        return v_upper
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """환경 설정 검증"""
        valid_envs = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"ENVIRONMENT는 {valid_envs} 중 하나여야 합니다.")
        return v_lower
    
    # =========================================================================
    # 유틸리티 메서드
    # =========================================================================
    def is_production(self) -> bool:
        """프로덕션 환경인지 확인"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """개발 환경인지 확인"""
        return self.ENVIRONMENT == "development"
    
    def get_api_url(self) -> str:
        """API URL 반환"""
        return f"http://{self.HOST}:{self.PORT}"
    
    class Config:
        """Pydantic 설정"""
        case_sensitive = True
        arbitrary_types_allowed = True


# =========================================================================
# 설정 객체 생성 (싱글톤)
# =========================================================================
settings = Settings()

# 초기화 시 설정 정보 출력 (개발 환경에서만)
if settings.is_development():
    print("=" * 80)
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📝 환경: {settings.ENVIRONMENT}")
    print(f"🌐 서버: {settings.get_api_url()}")
    print(f"🔍 디버그: {settings.DEBUG}")
    print(f"📊 로그 레벨: {settings.LOG_LEVEL}")
    print("=" * 80)
