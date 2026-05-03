from unittest.mock import MagicMock, patch
from src.infra.notifier import SlackNotifier

def test_slack_notifier_no_url():
    logger = MagicMock()
    notifier = SlackNotifier(webhook_url="", logger=logger)
    
    notifier.send_message("Hello")
    # URL이 없으면 info 로그를 남김
    logger.info.assert_called_once()
    assert "[Slack Mock]" in logger.info.call_args[0][0]

@patch("requests.post")
def test_slack_notifier_send_success(mock_post):
    mock_post.return_value.status_code = 200
    logger = MagicMock()
    notifier = SlackNotifier(webhook_url="http://fake.url", logger=logger)
    
    notifier.send_message("Hello")
    
    mock_post.assert_called_once()
    payload = mock_post.call_args[1]["json"]
    assert "Hello" in payload["text"]
    assert "🤖" in payload["text"]

@patch("requests.post")
def test_slack_notifier_send_alert(mock_post):
    mock_post.return_value.status_code = 200
    logger = MagicMock()
    notifier = SlackNotifier(webhook_url="http://fake.url", logger=logger)
    
    notifier.send_alert("Danger")
    
    payload = mock_post.call_args[1]["json"]
    assert "Danger" in payload["text"]
    assert "🚨" in payload["text"]
    assert "<!channel>" in payload["text"]

@patch("requests.post")
def test_slack_notifier_error_logging(mock_post):
    mock_post.return_value.status_code = 404
    mock_post.return_value.text = "Not Found"
    logger = MagicMock()
    notifier = SlackNotifier(webhook_url="http://fake.url", logger=logger)
    
    notifier.send_message("Hello")
    logger.error.assert_called_once()
    assert "404" in logger.error.call_args[0][0]
