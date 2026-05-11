# Models package

from app.models.user import User
from app.models.scan import Scan
from app.models.page import Page
from app.models.vulnerability import Vulnerability
from app.models.ai_result import AIResult
from app.models.chat_message import ChatMessage

__all__ = ['User', 'Scan', 'Page', 'Vulnerability', 'AIResult']
