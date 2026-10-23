# FestiveAI: Security, Privacy & Compliance Architecture

## 1. Sensitive Credential Encryption
- All OAuth Access Tokens and Refresh Tokens are encrypted before storage in the database using **Fernet (AES-128-CBC with HMAC-SHA256 authenticated encryption)**.
- Encryption keys are kept strictly in environment variables (`ENCRYPTION_KEY`) and are never committed to version control.
- Tokens are masked in API responses and console logging (`EAAB...d8e3`).

## 2. Minimum Platform Permissions
FestiveAI requests only the bare minimum platform scopes needed for feed publishing:
- **Instagram**: `instagram_basic`, `instagram_content_publish`, `pages_show_list`
- **LinkedIn**: `w_member_social`, `rw_organization_admin`

## 3. Rate Limit Handling & Token Expiration
- Platform response headers (e.g. `X-App-Usage` for Meta) are inspected for rate limit thresholds.
- If an authorization token expires or is revoked (error code 190 / 401), FestiveAI marks the campaign as `needs_authorization` and aborts retries to prevent account flagging.

## 4. Multi-Tenant Data Isolation
- Every database model references `organization_id` or `social_account_id`.
- FastAPI dependency injection (`get_current_user`) verifies organization boundaries across all queries.

## 5. Duplicate Prevention & Financial Safety
- Strict database constraints guarantee zero duplicate campaigns:
  `UNIQUE(social_account_id, festival_id, year)`
- Publishing attempts are checked against existing `platform_post_id` values before re-transmitting to network APIs.
