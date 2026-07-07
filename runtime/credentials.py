"""Bring-Your-Own-Key (BYOK) credential resolution.

This framework is shared publicly. It MUST NEVER embed or ship the owner's API
credentials, and it must never read them from a committed file. Every secret -
the Claude/Anthropic API key and any downstream tool credential (Vercel, Neon,
Clerk, Resend, a booking provider, a payment provider, ...) - is supplied by the *user running the
framework*, resolved here from (in priority order):

  1. an **injected config dict** (e.g. the dashboard passing a user's own keys
     in at runtime), then
  2. the **process environment** (``ANTHROPIC_API_KEY`` etc.).

There is no third source: no default value baked into code, no lookup of a
committed dotfile. If a required key is absent, :meth:`Credentials.require`
fails LOUD and CLEAR with an actionable message - it never silently proceeds or
substitutes a default.

Secrets are referenced **by name** only. Values are never written into any log,
error message, or emitted state ledger; :func:`mask` reduces a secret to at most
its last four characters for the rare case a diagnostic must mention it.
"""

from __future__ import annotations

import os
from typing import Dict, Mapping, Optional


class CredentialError(RuntimeError):
    """A required credential was not configured (BYOK). Actionable by design."""


# The env-var name each supported service's secret is resolved from. Only the
# NAMES live in code - never a value.
KNOWN_SERVICES: Dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "vercel": "VERCEL_TOKEN",
    "neon": "NEON_API_KEY",
    "clerk": "CLERK_SECRET_KEY",
    "resend": "RESEND_API_KEY",
    "booking_provider": "BOOKING_PROVIDER_API_KEY",
    "payment_provider": "PAYMENT_PROVIDER_API_KEY",
}


def mask(value: Optional[str]) -> str:
    """Redact a secret to at most its last four characters for safe logging.

    ``None``/empty -> ``"<unset>"``; short values are fully masked so nothing
    sensitive leaks even for tiny keys.
    """
    if not value:
        return "<unset>"
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]


class Credentials:
    """Env-first, then injected-dict credential source (BYOK).

    Construct with an optional ``overrides`` dict (highest priority) - this is
    how the future dashboard hands a user's own keys to the kernel without any
    secret ever touching the repo. Falls back to the process environment.
    """

    def __init__(self, overrides: Optional[Mapping[str, str]] = None, *,
                 environ: Optional[Mapping[str, str]] = None) -> None:
        # injected dict wins over the environment
        self._overrides: Dict[str, str] = dict(overrides or {})
        self._environ: Mapping[str, str] = (
            environ if environ is not None else os.environ)

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Return the secret for ``name`` (injected dict, then env), else
        ``default``. Never raises."""
        if name in self._overrides and self._overrides[name]:
            return self._overrides[name]
        val = self._environ.get(name)
        return val if val else default

    def require(self, name: str, *, service: Optional[str] = None) -> str:
        """Return the secret for ``name`` or raise a clear, actionable error.

        Never returns a default and never logs the value. The error names the
        env var to set and the injected-config alternative - the whole point of
        BYOK: the user supplies their own key, and the framework says exactly
        how when one is missing.
        """
        val = self.get(name)
        if val:
            return val
        svc = f" for {service}" if service else ""
        raise CredentialError(
            f"no API key configured{svc}: '{name}' is not set. "
            f"Set the {name} environment variable, or provide it in the app "
            f"(injected runtime config). This framework is bring-your-own-key "
            f"and ships no credentials of its own."
        )

    def require_service(self, service: str) -> str:
        """Require the secret for a known service by short name (e.g. 'payment_provider')."""
        try:
            env_name = KNOWN_SERVICES[service]
        except KeyError:
            raise CredentialError(
                f"unknown service {service!r}; known services: "
                f"{', '.join(sorted(KNOWN_SERVICES))}")
        return self.require(env_name, service=service)

    def has(self, name: str) -> bool:
        return bool(self.get(name))

    def masked(self, name: str) -> str:
        """The secret for ``name`` reduced to last-4 - safe to log."""
        return mask(self.get(name))
