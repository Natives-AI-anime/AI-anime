# -----------------------------------------------------------------------------
# config/settings.py
# -----------------------------------------------------------------------------
# 이 파일은 프로젝트의 "설정"을 담당합니다.
# .env 파일에 적힌 비밀 정보나 설정값을 불러와서, 파이썬 코드에서 변수처럼 쓸 수 있게 해줍니다.

import os
from dotenv import load_dotenv

# 1. .env 파일을 찾아서 내용을 불러옵니다.
# 이제 os.getenv("변수이름")을 쓰면 .env에 적힌 값을 가져올 수 있습니다.
load_dotenv()

class Settings:
    """
    프로젝트의 모든 설정을 모아둔 클래스입니다.
    다른 파일에서는 이 클래스를 불러와서 설정을 사용합니다.
    """
    
    # 프로젝트 기본 정보
    PROJECT_NAME: str = "AI Anime Generator"
    VERSION: str = "1.0.0"

    # 2. 환경 변수 가져오기
    # .env 파일에서 "GOOGLE_API_KEY"라는 이름의 값을 가져옵니다.
    # 만약 파일에 값이 없으면 "" (빈 문자열)을 대신 넣습니다.
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    # 필요하면 여기에 데이터베이스 주소 등을 계속 추가하면 됩니다.
    # DB_URL: str = os.getenv("DB_URL", "sqlite:///./test.db")

# 3. 설정 객체 생성
# 이 'settings' 변수를 다른 파일에서 import 해서 사용합니다.
settings = Settings()
