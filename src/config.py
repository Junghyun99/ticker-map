import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    def __init__(self):  # <--- [중요] 모든 설정 로직을 이 함수 안으로 넣어야 합니다.
        self.SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
        self.LOG_PATH = "logs/ci" if os.getenv("GITHUB_ACTIONS") == "true" else "logs/local"
