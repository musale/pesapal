"""Pesapal API client and api methods."""
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx

from pesapal_v3._exceptions import PesapalAuthError, PesapalIPNURLRegError
from pesapal_v3._types import (AccessToken, APIError, Environment,
                               IPNRegistration, IPNRegistrationError,
                               PesapalError)


class Pesapal:
    """Pesapal client."""

    _token_timeout = 5

    def __init__(
        self,
        *,
        consumer_key: str,
        consumer_secret: str,
        environment: Environment = "sandbox",
    ) -> None:
        if not consumer_key:
            raise ValueError("consumer_key cannot be empty")

        if not consumer_secret:
            raise ValueError("consumer_secret cannot be empty")

        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret

        if environment == "sandbox":
            self._base_url = "https://cybqa.pesapal.com/pesapalv3/api"
        else:
            self._base_url = "https://pay.pesapal.com/v3/api"

        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self._token = self._authenticate(
            consumer_key=self._consumer_key, consumer_secret=self._consumer_secret
        )
        self._instantiation_time = datetime.now()

    def _refresh_token(self) -> None:
        now = datetime.now()
        refresh = (
            now - self._instantiation_time > timedelta(minutes=self._token_timeout)
            or now.minute != self._instantiation_time.minute
        )
        if refresh:
            self._token = self._authenticate(
                consumer_key=self._consumer_key, consumer_secret=self._consumer_secret
            )

    def _authenticate(
        self, *, consumer_key: str, consumer_secret: str
    ) -> Optional[AccessToken]:
        with httpx.Client(base_url=self._base_url) as client:
            data = {"consumer_key": consumer_key, "consumer_secret": consumer_secret}
            client_resp = client.post(
                "/Auth/RequestToken", headers=self._headers, json=data
            )
            response = client_resp.json()
            error = response.get("error", None)
            if error:
                raise PesapalAuthError(
                    error=error, status=response.get("status", "500")
                )
            token = response.get("token", "")
            self._headers.update({"Authorization": f"Bearer {token}"})
            access_token: Optional[AccessToken] = AccessToken(**response)
        return access_token

    def update_headers(self, *, headers: Dict[str, str]) -> None:
        """Updates the header values."""
        self._headers.update(headers)

    def register_ipn_url(
        self, *, ipn_url: str, ipn_notification_type: str = "GET"
    ) -> IPNRegistration:
        """Register the Instant Payment Notification callback URL.

        Arguments:
            ipn_url(str): the URL to register as a callback URL.
            ipn_notification_type(str): the http request method Pesapal will
                use when triggering the IPN alert. Can be GET or POST.
                Default is GET.
        """
        if not ipn_url:
            raise ValueError("ipn_url cannot be empty.")

        if not ipn_notification_type:
            raise ValueError("ipn_notification_type cannot be empty.")

        self._refresh_token()
        with httpx.Client(base_url=self._base_url) as client:
            data = {
                "url": ipn_url,
                "ipn_notification_type": ipn_notification_type,
            }
            client_resp = client.post(
                "/URLSetup/RegisterIPN", headers=self._headers, json=data
            )
            response = client_resp.json()

        message = response.get("message", None)
        if isinstance(message, str):
            message = json.loads(message)

        if isinstance(message, dict):
            error = message.get("error", None)
            status = message.get("status", "500")
            if message and error:
                error_msg = PesapalError(**error)
                raise PesapalIPNURLRegError(error=error_msg, status=status)
        ipn: IPNRegistration = IPNRegistration(**response)
        return ipn
