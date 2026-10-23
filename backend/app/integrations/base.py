from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SocialPlatformAdapter(ABC):
    """
    Abstract interface for all social media platform publishing adapters.
    Ensures platform-agnostic campaign orchestration.
    """

    @abstractmethod
    def verify_credentials(self, access_token: str, account_id: str) -> bool:
        """Verifies if the stored token has valid publishing scope and is not expired."""
        pass

    @abstractmethod
    def publish_image_post(
        self,
        access_token: str,
        platform_account_id: str,
        image_url: str,
        caption: str,
        is_mock: bool = False
    ) -> Dict[str, Any]:
        """
        Publishes an image post with caption.
        Returns a dictionary containing:
        - success: bool
        - platform_post_id: str (if success)
        - response_data: dict
        - error_message: str (if failed)
        - error_code: str (if failed)
        """
        pass
