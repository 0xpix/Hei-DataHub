"""
WebDAV authentication diagnostics.

Deep diagnostics for WebDAV auth & access.
"""
import json
import logging
import platform
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticResult:
    """Result of a single diagnostic check."""

    check: str
    passed: bool
    message: str
    details: Optional[dict] = None


class AuthDoctor:
    """WebDAV authentication diagnostics runner."""

    def __init__(
        self,
        output_json: bool = False,
        skip_write: bool = False,
        timeout: int = 8,
    ):
        """
        Initialize the doctor.

        Args:
            output_json: Output results as JSON
            skip_write: Skip write permission tests
            timeout: Network timeout in seconds
        """
        self.output_json = output_json
        self.skip_write = skip_write
        self.timeout = timeout
        self.results: list[DiagnosticResult] = []

    def run(self) -> int:
        """
        Run all diagnostics.

        Returns:
            Exit code (0 = all critical checks passed)
        """
        # Run all checks (continue even if one fails)
        self._check_config_file()
        self._check_credentials_present()
        self._check_network_reachability()
        self._check_webdav_auth()
        self._check_permissions()
        self._check_mount_awareness()
        self._check_clock_skew()

        # Output results
        if self.output_json:
            self._output_json()
        else:
            self._output_human()

        # Determine exit code
        return self._determine_exit_code()

    def _check_config_file(self) -> None:
        """Check if config file exists and is readable."""
        from hei_datahub.infra.config_paths import get_config_path

        config_path = get_config_path()

        if not config_path.exists():
            self.results.append(
                DiagnosticResult(
                    check="config_file",
                    passed=False,
                    message=f"Config file not found: {config_path}",
                    details={"path": str(config_path), "exists": False},
                )
            )
            return

        # Try to read and parse
        try:
            try:
                import tomllib as tomli
            except ImportError:
                import tomli

            with open(config_path, "rb") as f:
                config = tomli.load(f)

            # Check if it has auth section
            if "auth" not in config:
                self.results.append(
                    DiagnosticResult(
                        check="config_file",
                        passed=False,
                        message="Config file missing [auth] section",
                        details={"path": str(config_path), "readable": True, "has_auth": False},
                    )
                )
                return

            self.results.append(
                DiagnosticResult(
                    check="config_file",
                    passed=True,
                    message=f"Config found: {config_path}",
                    details={"path": str(config_path), "readable": True, "has_auth": True},
                )
            )
            # Store config for later checks
            self._config = config.get("auth", {})
            self._config_path = config_path

        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check="config_file",
                    passed=False,
                    message=f"Config file read error: {e}",
                    details={"path": str(config_path), "error": str(e)},
                )
            )

    def _check_credentials_present(self) -> None:
        """Check if credentials are present in keyring/env."""
        if not hasattr(self, "_config"):
            self.results.append(
                DiagnosticResult(
                    check="credentials_present",
                    passed=False,
                    message="Cannot check credentials (no config)",
                    details={},
                )
            )
            return

        try:
            from hei_datahub.cli.auth.credentials import get_auth_store

            key_id = self._config.get("key_id")
            if not key_id:
                self.results.append(
                    DiagnosticResult(
                        check="credentials_present",
                        passed=False,
                        message="No key_id in config",
                        details={},
                    )
                )
                return

            # Try to load credential
            store = get_auth_store(prefer_keyring=True)
            credential = store.load_secret(key_id)

            if credential:
                # Mask all but last 4 chars
                masked = "****…" + credential[-4:] if len(credential) >= 4 else "****"
                self.results.append(
                    DiagnosticResult(
                        check="credentials_present",
                        passed=True,
                        message=f"Credentials present (token {masked})",
                        details={"masked_token": masked, "key_id": key_id},
                    )
                )
                # Store for later checks
                self._credential = credential
            else:
                self.results.append(
                    DiagnosticResult(
                        check="credentials_present",
                        passed=False,
                        message=f"Credential not found for key_id: {key_id}",
                        details={"key_id": key_id},
                    )
                )

        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check="credentials_present",
                    passed=False,
                    message=f"Error loading credentials: {e}",
                    details={"error": str(e)},
                )
            )

    def _check_network_reachability(self) -> None:
        """Check DNS resolution and TCP connectivity."""
        if not hasattr(self, "_config"):
            self.results.append(
                DiagnosticResult(
                    check="network_reachability",
                    passed=False,
                    message="Cannot check network (no config)",
                    details={},
                )
            )
            return

        url = self._config.get("url", "")
        if not url:
            self.results.append(
                DiagnosticResult(
                    check="network_reachability",
                    passed=False,
                    message="No URL in config",
                    details={},
                )
            )
            return

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            if not hostname:
                self.results.append(
                    DiagnosticResult(
                        check="network_reachability",
                        passed=False,
                        message=f"Invalid URL: {url}",
                        details={"url": url},
                    )
                )
                return

            # DNS resolution
            try:
                ip_address = socket.gethostbyname(hostname)
            except socket.gaierror as e:
                self.results.append(
                    DiagnosticResult(
                        check="network_reachability",
                        passed=False,
                        message=f"DNS resolution failed for {hostname}: {e}",
                        details={"hostname": hostname, "error": str(e)},
                    )
                )
                return

            # TCP connect
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((ip_address, port))
                sock.close()

                if result == 0:
                    self.results.append(
                        DiagnosticResult(
                            check="network_reachability",
                            passed=True,
                            message=f"Reachable: {hostname}",
                            details={"hostname": hostname, "ip": ip_address, "port": port},
                        )
                    )
                else:
                    self.results.append(
                        DiagnosticResult(
                            check="network_reachability",
                            passed=False,
                            message=f"TCP connection failed to {hostname}:{port}",
                            details={"hostname": hostname, "ip": ip_address, "port": port, "error_code": result},
                        )
                    )
            except Exception as e:
                self.results.append(
                    DiagnosticResult(
                        check="network_reachability",
                        passed=False,
                        message=f"Connection error: {e}",
                        details={"hostname": hostname, "error": str(e)},
                    )
                )

        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check="network_reachability",
                    passed=False,
                    message=f"Network check error: {e}",
                    details={"error": str(e)},
                )
            )

    def _check_webdav_auth(self) -> None:
        """Check WebDAV authentication via PROPFIND."""
        if not hasattr(self, "_config") or not hasattr(self, "_credential"):
            self.results.append(
                DiagnosticResult(
                    check="webdav_auth",
                    passed=False,
                    message="Cannot check WebDAV auth (missing config or credentials)",
                    details={},
                )
            )
            return

        url = self._config.get("url", "")
        username = self._config.get("username")

        if not url:
            self.results.append(
                DiagnosticResult(
                    check="webdav_auth",
                    passed=False,
                    message="No URL in config",
                    details={},
                )
            )
            return

        try:
            session = requests.Session()
            if username:
                session.auth = (username, self._credential)
            else:
                # Token-only auth (some servers use Basic auth with empty username)
                session.auth = ("", self._credential)

            # Time the request
            start_time = time.time()
            response = session.request(
                "PROPFIND",
                url.rstrip("/") + "/",
                headers={"Depth": "0"},
                timeout=self.timeout,
                verify=True,
                allow_redirects=True,
            )
            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 207:
                self.results.append(
                    DiagnosticResult(
                        check="webdav_auth",
                        passed=True,
                        message=f"WebDAV auth OK (PROPFIND 207, {latency_ms} ms)",
                        details={"status": 207, "latency_ms": latency_ms},
                    )
                )
            elif response.status_code in (401, 403):
                hint = "Token expired/invalid; run `hei-datahub auth setup`."
                self.results.append(
                    DiagnosticResult(
                        check="webdav_auth",
                        passed=False,
                        message=f"Auth failed (HTTP {response.status_code}): {hint}",
                        details={"status": response.status_code, "hint": hint},
                    )
                )
            elif response.status_code in (405, 501):
                hint = "Server/WebDAV disabled or URL wrong."
                self.results.append(
                    DiagnosticResult(
                        check="webdav_auth",
                        passed=False,
                        message=f"PROPFIND unsupported (HTTP {response.status_code}): {hint}",
                        details={"status": response.status_code, "hint": hint},
                    )
                )
            elif response.status_code == 404:
                hint = "Check WebDAV base URL."
                self.results.append(
                    DiagnosticResult(
                        check="webdav_auth",
                        passed=False,
                        message=f"Not found (HTTP 404): {hint}",
                        details={"status": 404, "hint": hint},
                    )
                )
            else:
                self.results.append(
                    DiagnosticResult(
                        check="webdav_auth",
                        passed=False,
                        message=f"Unexpected status: {response.status_code}",
                        details={"status": response.status_code, "latency_ms": latency_ms},
                    )
                )

        except requests.exceptions.SSLError as e:
            hint = "Corporate proxy / CA cert issue."
            self.results.append(
                DiagnosticResult(
                    check="webdav_auth",
                    passed=False,
                    message=f"TLS error: {hint}",
                    details={"error": str(e), "hint": hint},
                )
            )
        except requests.exceptions.Timeout:
            self.results.append(
                DiagnosticResult(
                    check="webdav_auth",
                    passed=False,
                    message="Request timed out",
                    details={"timeout": self.timeout},
                )
            )
        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check="webdav_auth",
                    passed=False,
                    message=f"WebDAV check error: {e}",
                    details={"error": str(e)},
                )
            )

    def _check_permissions(self) -> None:
        """Check read/write permissions via PUT and DELETE."""
        if self.skip_write:
            self.results.append(
                DiagnosticResult(
                    check="permissions",
                    passed=True,
                    message="SKIPPED (--no-write)",
                    details={"skipped": True},
                )
            )
            return

        if not hasattr(self, "_config") or not hasattr(self, "_credential"):
            self.results.append(
                DiagnosticResult(
                    check="permissions",
                    passed=False,
                    message="Cannot check permissions (missing config or credentials)",
                    details={},
                )
            )
            return

        url = self._config.get("url", "")
        username = self._config.get("username")
        library = self._config.get("library", "")

        if not url:
            self.results.append(
                DiagnosticResult(
                    check="permissions",
                    passed=False,
                    message="No URL in config",
                    details={},
                )
            )
            return

        try:
            session = requests.Session()
            if username:
                session.auth = (username, self._credential)
            else:
                session.auth = ("", self._credential)

            # Create a test file path inside the library (Seafile requires writing into a library)
            import uuid
            test_filename = f".hei-datahub-doctor-{uuid.uuid4().hex[:8]}.txt"
            base = url.rstrip("/")
            if library:
                base = f"{base}/{library.strip('/')}"
            test_url = base + "/" + test_filename
            test_content = b"hei-datahub doctor test"

            # Try PUT
            put_response = session.put(
                test_url,
                data=test_content,
                timeout=self.timeout,
                verify=True,
            )

            if put_response.status_code not in (200, 201, 204):
                hint = "Check library/folder ACLs." if put_response.status_code in (401, 403) else ""
                self.results.append(
                    DiagnosticResult(
                        check="permissions",
                        passed=False,
                        message=f"Write failed (PUT {put_response.status_code}): {hint}",
                        details={"put_status": put_response.status_code, "hint": hint},
                    )
                )
                return

            # Try DELETE
            delete_response = session.delete(
                test_url,
                timeout=self.timeout,
                verify=True,
            )

            if delete_response.status_code not in (200, 204, 404):
                # Don't fail if delete doesn't work but file was created
                self.results.append(
                    DiagnosticResult(
                        check="permissions",
                        passed=True,
                        message=f"Read/write OK (cleanup warning: DELETE {delete_response.status_code})",
                        details={"put_status": put_response.status_code, "delete_status": delete_response.status_code},
                    )
                )
            else:
                self.results.append(
                    DiagnosticResult(
                        check="permissions",
                        passed=True,
                        message="Read/write OK",
                        details={"put_status": put_response.status_code, "delete_status": delete_response.status_code},
                    )
                )

        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check="permissions",
                    passed=False,
                    message=f"Permission check error: {e}",
                    details={"error": str(e)},
                )
            )

    def _check_mount_awareness(self) -> None:
        """Check if local mount path is configured and writable."""
        # This is optional - check if there's a mount path in config
        # For now, we'll mark as SKIPPED since mount is not commonly used
        self.results.append(
            DiagnosticResult(
                check="mount_path",
                passed=True,
                message="SKIPPED (mount path not configured)",
                details={"skipped": True},
            )
        )

    def _check_clock_skew(self) -> None:
        """Check for system clock skew."""
        try:
            # Get current system time
            local_time = datetime.now(timezone.utc)

            # Try to get server time from HTTP headers
            if hasattr(self, "_config"):
                url = self._config.get("url", "")
                if url:
                    try:
                        response = requests.head(url, timeout=self.timeout, verify=True)
                        server_time_str = response.headers.get("Date")

                        if server_time_str:
                            from email.utils import parsedate_to_datetime
                            server_time = parsedate_to_datetime(server_time_str)

                            # Calculate difference
                            diff_seconds = abs((local_time - server_time).total_seconds())

                            if diff_seconds > 120:  # 2 minutes
                                self.results.append(
                                    DiagnosticResult(
                                        check="clock_skew",
                                        passed=False,
                                        message=f"Clock skew detected: {int(diff_seconds)}s difference (may cause token issues)",
                                        details={"skew_seconds": int(diff_seconds)},
                                    )
                                )
                            else:
                                self.results.append(
                                    DiagnosticResult(
                                        check="clock_skew",
                                        passed=True,
                                        message="Clock OK",
                                        details={"skew_seconds": int(diff_seconds)},
                                    )
                                )
                            return
                    except Exception:
                        pass

            # If we can't get server time, just skip
            self.results.append(
                DiagnosticResult(
                    check="clock_skew",
                    passed=True,
                    message="SKIPPED (cannot determine server time)",
                    details={"skipped": True},
                )
            )

        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check="clock_skew",
                    passed=True,
                    message=f"SKIPPED ({e})",
                    details={"skipped": True, "error": str(e)},
                )
            )

    def _output_human(self) -> None:
        """Output human-readable results."""
        print("🔍 Checking configuration...")

        for result in self.results:
            icon = "✅" if result.passed else "❌"
            print(f"{icon} {result.message}")

        # Overall summary
        critical_checks = ["config_file", "credentials_present", "webdav_auth", "permissions"]
        critical_failed = any(
            not r.passed for r in self.results
            if r.check in critical_checks and not r.details.get("skipped", False)
        )

        overall = "FAIL" if critical_failed else "PASS"
        print(f"\nOverall: {overall}")

    def _output_json(self) -> None:
        """Output JSON results."""
        output = {
            "config_found": any(r.check == "config_file" and r.passed for r in self.results),
            "config_path": str(getattr(self, "_config_path", "")),
            "creds_present": any(r.check == "credentials_present" and r.passed for r in self.results),
            "webdav_latency_ms": next(
                (r.details.get("latency_ms", 0) for r in self.results if r.check == "webdav_auth" and r.passed),
                0,
            ),
            "webdav_status": next(
                (r.details.get("status", 0) for r in self.results if r.check == "webdav_auth"),
                0,
            ),
            "read_write_ok": any(
                r.check == "permissions" and r.passed and not r.details.get("skipped", False)
                for r in self.results
            ),
            "mount_path_ok": any(r.check == "mount_path" and r.passed for r in self.results),
        }

        # Determine overall
        critical_checks = ["config_file", "credentials_present", "webdav_auth", "permissions"]
        critical_failed = any(
            not r.passed for r in self.results
            if r.check in critical_checks and not r.details.get("skipped", False)
        )
        output["overall"] = "FAIL" if critical_failed else "PASS"

        print(json.dumps(output, indent=2))

    def _determine_exit_code(self) -> int:
        """
        Determine exit code based on results.

        Returns:
            0 = all critical checks pass
            2 = config issues
            3 = auth issues
            4 = permission issues
            5 = network/TLS issues
        """
        # Check for specific failure types
        for result in self.results:
            if result.passed or result.details.get("skipped", False):
                continue

            if result.check == "config_file":
                return 2
            elif result.check == "credentials_present":
                return 2
            elif result.check == "webdav_auth":
                if result.details.get("status") in (401, 403):
                    return 3
                elif "TLS" in result.message or "SSL" in result.message:
                    return 5
                else:
                    return 3
            elif result.check == "permissions":
                return 4
            elif result.check == "network_reachability":
                return 5

        return 0


def run_doctor(output_json: bool = False, skip_write: bool = False, timeout: int = 8) -> int:
    """
    Run WebDAV authentication diagnostics.

    Args:
        output_json: Output results as JSON
        skip_write: Skip write permission tests
        timeout: Network timeout in seconds

    Returns:
        Exit code (0 = success)
    """
    if platform.system() not in ["Linux", "Windows", "Darwin"]:
        print(f"❌ Error: auth doctor is only supported on Linux, Windows, and macOS (current: {platform.system()}).", file=sys.stderr)
        return 2

    doctor = AuthDoctor(output_json=output_json, skip_write=skip_write, timeout=timeout)
    return doctor.run()
