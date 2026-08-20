import hmac
import hashlib
import secrets
import base64
import time
import struct
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.identity import UserSession, MFAEnrollment
from backend.app.models.user import User
from backend.app.core.exceptions import AuthenticationError, SentinelAIException

logger = logging.getLogger("SentinelAI.Identity")


class IdentityService:
    """Enterprise authentication, TOTP MFA, active session management, and device tracking."""

    @classmethod
    def _hash_token(cls, raw_token: str) -> str:
        """Computes SHA-256 digest of session or recovery token."""
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    # -----------------------------------------------------------------------
    # TOTP MFA (RFC 6238 implementation without mandatory external C-libs)
    # -----------------------------------------------------------------------

    @classmethod
    def generate_totp_secret(cls) -> str:
        """Generates a 160-bit Base32-encoded secret for RFC 6238 TOTP."""
        random_bytes = secrets.token_bytes(20)
        return base64.b32encode(random_bytes).decode("utf-8").replace("=", "")

    @classmethod
    def generate_recovery_codes(cls, count: int = 8) -> Tuple[List[str], List[str]]:
        """Generates a list of plain recovery codes and their SHA-256 hashes."""
        plain_codes = [f"{secrets.token_hex(4)}-{secrets.token_hex(4)}".upper() for _ in range(count)]
        hashed_codes = [cls._hash_token(c) for c in plain_codes]
        return plain_codes, hashed_codes

    @classmethod
    def compute_totp(cls, secret_base32: str, time_step: int = 30, for_time: Optional[int] = None) -> str:
        """Computes current 6-digit TOTP code for the given Base32 secret."""
        t = for_time or int(time.time())
        intervals = int(t // time_step)
        
        # Pad Base32 secret if necessary
        padded_secret = secret_base32 + "=" * ((8 - len(secret_base32) % 8) % 8)
        key = base64.b32decode(padded_secret, casefold=True)
        msg = struct.pack(">Q", intervals)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        
        offset = h[-1] & 0x0F
        truncated_hash = struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF
        code = str(truncated_hash % 1000000).zfill(6)
        return code

    @classmethod
    def verify_totp(cls, secret_base32: str, code: str, window: int = 1) -> bool:
        """Validates a 6-digit TOTP code against secret with a +/- window for clock drift."""
        if not code or len(code.strip()) != 6:
            return False
        clean_code = code.strip()
        current_time = int(time.time())

        # Check current interval and +/- window intervals
        for step_offset in range(-window, window + 1):
            check_time = current_time + (step_offset * 30)
            expected = cls.compute_totp(secret_base32, for_time=check_time)
            if hmac.compare_digest(expected, clean_code):
                return True
        return False

    @classmethod
    async def enroll_mfa(cls, db: AsyncSession, user_id: str) -> Tuple[str, List[str], str]:
        """
        Starts MFA enrollment. Returns (secret_base32, plain_recovery_codes, otpauth_uri).
        """
        secret = cls.generate_totp_secret()
        plain_codes, hashed_codes = cls.generate_recovery_codes()

        stmt = select(MFAEnrollment).where(MFAEnrollment.user_id == user_id)
        res = await db.execute(stmt)
        enrollment = res.scalar_one_or_none()

        if not enrollment:
            enrollment = MFAEnrollment(
                user_id=user_id,
                mfa_type="TOTP",
                encrypted_secret=secret,
                is_verified=False,
                recovery_codes_hash_json=hashed_codes
            )
            db.add(enrollment)
        else:
            enrollment.encrypted_secret = secret
            enrollment.is_verified = False
            enrollment.recovery_codes_hash_json = hashed_codes
            enrollment.updated_at = datetime.now(timezone.utc)

        await db.flush()
        otpauth_uri = f"otpauth://totp/Aegivanta:{user_id}?secret={secret}&issuer=Aegivanta"
        return secret, plain_codes, otpauth_uri

    @classmethod
    async def verify_and_activate_mfa(cls, db: AsyncSession, user_id: str, code: str) -> bool:
        """Verifies initial setup code and marks MFA as active."""
        stmt = select(MFAEnrollment).where(MFAEnrollment.user_id == user_id)
        res = await db.execute(stmt)
        enrollment = res.scalar_one_or_none()
        if not enrollment:
            return False

        if cls.verify_totp(enrollment.encrypted_secret, code):
            enrollment.is_verified = True
            enrollment.updated_at = datetime.now(timezone.utc)
            await db.flush()
            return True
        return False

    @classmethod
    async def validate_mfa_login(cls, db: AsyncSession, user_id: str, code_or_recovery: str) -> bool:
        """Validates TOTP code or single-use recovery code during login."""
        stmt = select(MFAEnrollment).where(
            and_(
                MFAEnrollment.user_id == user_id,
                MFAEnrollment.is_verified == True
            )
        )
        res = await db.execute(stmt)
        enrollment = res.scalar_one_or_none()
        if not enrollment:
            return True  # MFA not enrolled

        clean_token = code_or_recovery.strip()

        # 1. Check TOTP Code
        if len(clean_token) == 6 and clean_token.isdigit():
            if cls.verify_totp(enrollment.encrypted_secret, clean_token):
                return True

        # 2. Check Recovery Code
        token_hash = cls._hash_token(clean_token.upper())
        recovery_hashes = list(enrollment.recovery_codes_hash_json or [])
        if token_hash in recovery_hashes:
            # Burn used recovery code
            recovery_hashes.remove(token_hash)
            enrollment.recovery_codes_hash_json = recovery_hashes
            enrollment.updated_at = datetime.now(timezone.utc)
            await db.flush()
            logger.info("User %s used emergency recovery code for MFA authentication", user_id)
            return True

        return False

    # -----------------------------------------------------------------------
    # Active Session Tracking & Device Fingerprinting
    # -----------------------------------------------------------------------

    @classmethod
    async def create_user_session(
        cls,
        db: AsyncSession,
        user_id: str,
        organization_id: Optional[str],
        ip_address: str,
        user_agent: str,
        session_duration_minutes: int = 480
    ) -> Tuple[UserSession, str]:
        """Creates and tracks an active user session."""
        raw_session_token = f"sess_{secrets.token_hex(32)}"
        token_hash = cls._hash_token(raw_session_token)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=session_duration_minutes)

        # Check for suspicious new IP/device patterns
        stmt_prev = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.ip_address != ip_address
            )
        ).limit(1)
        res_prev = await db.execute(stmt_prev)
        is_suspicious = (res_prev.scalar_one_or_none() is not None and ip_address not in ["127.0.0.1", "localhost"])

        session = UserSession(
            user_id=user_id,
            organization_id=organization_id,
            session_token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent[:500],
            device_fingerprint=hashlib.sha256(f"{ip_address}:{user_agent}".encode()).hexdigest()[:16],
            is_active=True,
            is_suspicious=is_suspicious,
            last_activity_at=now,
            expires_at=expires_at
        )
        db.add(session)
        await db.flush()
        return session, raw_session_token

    @classmethod
    async def list_active_sessions(cls, db: AsyncSession, user_id: str) -> List[UserSession]:
        """Returns all unexpired, active sessions for user."""
        now = datetime.now(timezone.utc)
        stmt = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > now
            )
        ).order_by(UserSession.last_activity_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def revoke_session(cls, db: AsyncSession, session_id: str, user_id: str) -> bool:
        """Revokes a specific session."""
        stmt = select(UserSession).where(
            and_(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            )
        )
        res = await db.execute(stmt)
        sess = res.scalar_one_or_none()
        if not sess:
            return False

        sess.is_active = False
        await db.flush()
        return True
