import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.campaign import PublishingCampaign, PublishingAttempt, GeneratedCreative
from app.models.account import SocialAccount, OAuthCredential
from app.integrations.instagram import InstagramAdapter
from app.integrations.linkedin import LinkedInAdapter
from app.core.encryption import decrypt_secret

class PublishingService:
    @staticmethod
    def get_adapter(platform: str):
        if platform.lower() == "instagram":
            return InstagramAdapter()
        elif platform.lower() == "linkedin":
            return LinkedInAdapter()
        else:
            return InstagramAdapter()

    @staticmethod
    def publish_campaign(
        db: Session,
        campaign: PublishingCampaign,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Executes idempotent publishing with exponential backoff and telemetry recording.
        Guarantee: Never publishes twice if a platform_post_id is already assigned.
        """
        # Idempotency Gatekeeper: Check if already published
        if campaign.status == "published":
            existing_attempt = (
                db.query(PublishingAttempt)
                .filter_by(campaign_id=campaign.id, status="success")
                .first()
            )
            platform_id = existing_attempt.platform_post_id if existing_attempt else None
            return {
                "success": True,
                "message": "Campaign has already been published. Duplicate publish prevented.",
                "campaign_id": campaign.id,
                "platform_post_id": platform_id,
                "status": "published"
            }

        account = campaign.social_account
        creative = (
            db.query(GeneratedCreative)
            .filter_by(campaign_id=campaign.id, is_selected=True)
            .order_by(GeneratedCreative.version.desc())
            .first()
        )

        if not creative:
            campaign.status = "failed"
            campaign.error_message = "No generated creative available for publication."
            db.commit()
            return {"success": False, "error": campaign.error_message}

        # Check OAuth credentials
        creds = db.query(OAuthCredential).filter_by(social_account_id=account.id).first()
        if not creds:
            campaign.status = "needs_authorization"
            campaign.error_message = "No OAuth credentials found for account."
            db.commit()
            return {"success": False, "error": campaign.error_message}

        decrypted_token = decrypt_secret(creds.encrypted_access_token)
        is_mock_token = decrypted_token.startswith("mock_") or account.status == "mock"

        # Update status to publishing
        campaign.status = "publishing"
        db.commit()

        adapter = PublishingService.get_adapter(account.platform)
        caption_full = f"{creative.caption_text}\n\n{' '.join(json.loads(creative.hashtags or '[]'))}"

        attempt_count = db.query(PublishingAttempt).filter_by(campaign_id=campaign.id).count() + 1
        attempt = PublishingAttempt(
            campaign_id=campaign.id,
            attempt_number=attempt_count,
            started_at=datetime.now(timezone.utc),
            status="in_progress"
        )
        db.add(attempt)
        db.commit()

        # Execute publish with retry backoff
        last_error = None
        result = None

        for attempt_idx in range(1, max_retries + 1):
            result = adapter.publish_image_post(
                access_token=decrypted_token,
                platform_account_id=account.platform_account_id,
                image_url=creative.image_url,
                caption=caption_full,
                is_mock=is_mock_token
            )

            if result.get("success"):
                # Succeeded!
                platform_id = result.get("platform_post_id")
                attempt.status = "success"
                attempt.platform_post_id = platform_id
                attempt.platform_response = json.dumps(result.get("response_data", {}))
                attempt.finished_at = datetime.now(timezone.utc)

                campaign.status = "published"
                campaign.actual_publish_time = datetime.now(timezone.utc)
                campaign.error_message = None
                db.commit()
                return {
                    "success": True,
                    "platform_post_id": platform_id,
                    "campaign_id": campaign.id,
                    "status": "published"
                }
            else:
                last_error = result.get("error_message", "Unknown publishing error")
                attempt.error_code = result.get("error_code")
                attempt.error_traceback = last_error
                # If error is auth expired or permission revoked, don't keep retrying
                if result.get("error_code") in ["190", "401", "UNAUTHORIZED"]:
                    campaign.status = "needs_authorization"
                    campaign.error_message = f"Platform authorization error: {last_error}"
                    attempt.status = "auth_expired"
                    attempt.finished_at = datetime.now(timezone.utc)
                    db.commit()
                    return {"success": False, "error": campaign.error_message}

                # Exponential backoff before next retry
                if attempt_idx < max_retries:
                    time.sleep(2 ** attempt_idx)

        # Retries exhausted
        attempt.status = "failed"
        attempt.finished_at = datetime.now(timezone.utc)
        campaign.status = "failed"
        campaign.error_message = f"Publishing failed after {max_retries} attempts: {last_error}"
        campaign.retry_count = attempt_count
        db.commit()

        return {"success": False, "error": campaign.error_message}
