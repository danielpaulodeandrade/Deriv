
import base64
import binascii
import hashlib
import hmac
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


NONCE_SIZE = 12
TAG_SIZE = 16
VERSION = b"\x01"


def _get_cipher() -> AESGCM:
    try:
        key = base64.b64decode(
            settings.DATA_ENCRYPTION_KEY,
            validate=True,
        )
    except (ValueError, binascii.Error) as exc:
        raise RuntimeError(
            "DATA_ENCRYPTION_KEY must be valid Base64"
        ) from exc

    if len(key) != 32:
        raise RuntimeError(
            "DATA_ENCRYPTION_KEY must contain exactly 32 bytes"
        )

    return AESGCM(key)


def encrypt_secret(value: str) -> bytes:
    """Encrypt a secret using AES-256-GCM."""

    nonce = secrets.token_bytes(NONCE_SIZE)
    cipher = _get_cipher()

    ciphertext = cipher.encrypt(
        nonce,
        value.encode("utf-8"),
        VERSION,
    )

    return VERSION + nonce + ciphertext


def decrypt_secret(encrypted: bytes) -> str:
    """Decrypt and authenticate an AES-256-GCM secret."""

    minimum_size = 1 + NONCE_SIZE + TAG_SIZE

    if len(encrypted) < minimum_size:
        raise ValueError("Invalid encrypted data")

    version = encrypted[:1]

    if version != VERSION:
        raise ValueError("Unsupported encryption version")

    nonce = encrypted[1:1 + NONCE_SIZE]
    ciphertext = encrypted[1 + NONCE_SIZE:]

    try:
        plaintext = _get_cipher().decrypt(
            nonce,
            ciphertext,
            version,
        )
    except InvalidTag as exc:
        raise ValueError(
            "Encrypted data authentication failed"
        ) from exc

    return plaintext.decode("utf-8")


def generate_token() -> str:
    """Generate a cryptographically secure random token."""

    return secrets.token_urlsafe(32)


def hash_token(token: str) -> bytes:
    """Generate a SHA-256 digest suitable for BYTEA storage."""

    return hashlib.sha256(
        token.encode("utf-8")
    ).digest()


def verify_token(token: str, stored_hash: bytes) -> bool:
    """Compare a token against its stored SHA-256 digest."""

    calculated_hash = hash_token(token)

    return hmac.compare_digest(
        calculated_hash,
        stored_hash,
    )
