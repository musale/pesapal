"""Custom types for Pesapal SDK."""
from typing import Literal, NamedTuple, TypeAlias

Environment: TypeAlias = Literal["sandbox", "production"]


class PesapalError(NamedTuple):
    """A pesapal API access error"""

    error_type: str
    code: str
    message: str

    def __repr__(self) -> str:
        return (
            f"error_type: {self.error_type}, code: {self.code}, message: {self.message}"
        )


class AccessToken(NamedTuple):
    """The response of the returned token."""

    token: str
    expiryDate: str
    error: PesapalError
    status: str
    message: str


class APIError(NamedTuple):
    """Error response from an authenticated API call."""

    error: PesapalError


class IPNRegistration(NamedTuple):
    """The response from a successful IPN URL registration."""

    id: int
    url: str
    ipn_id: str
    status: str
    ipn_status: int
    created_date: str
    error: PesapalError
    notification_type: int
    ipn_status_decription: str
    ipn_notification_type_description: str


class IPNRegistrationError(NamedTuple):
    """The response from a failed IPN URL registration."""

    status: str
    message: APIError
