
import requests
from src.core.interfaces import INotifier

class SlackNotifier(INotifier):
    def __init__(self, webhook_url: str, logger):
        self.webhook_url = webhook_url
        self.logger = logger

    def send_message(self, message: str) -> None:
        # 일반 메시지
        self._send(f"🤖 *[SolidQuant]*\n{message}")

    def send_alert(self, message: str) -> None:
        # 긴급 알림 (channel 전체 호출)
        self._send(f"🚨 *[WARNING]* <!channel>\n{message}")

    def _send(self, text: str):
        if not self.webhook_url:
            # URL이 없으면(테스트 환경 등) 콘솔에만 출력
            msg = f"[Slack Mock] {text}"
            self.logger.info(msg)
            
            return

        try:
            # 슬랙 Webhook은 JSON Payload를 사용
            payload = {"text": text}
            response = requests.post(
                self.webhook_url, 
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code != 200:
                error_msg = f"[Slack Error] Status: {response.status_code}, Body: {response.text}"
                # [핵심] 파일에 기록 남기기
                self.logger.error(error_msg)

        except Exception as e:
            error_msg = f"[Slack Error] Connection failed: {e}"
            # [핵심] 파일에 기록 남기기
            self.logger.error(error_msg)
            