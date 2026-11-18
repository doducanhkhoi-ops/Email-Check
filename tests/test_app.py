import email
import importlib
import json
import os
import sys
import tempfile
import types
import unittest
from email.message import EmailMessage
from unittest.mock import MagicMock, patch


def _ensure_google_genai_stub():
    if "google.genai" in sys.modules:
        return
    google_pkg = sys.modules.setdefault("google", types.ModuleType("google"))
    genai_mod = types.ModuleType("google.genai")
    genai_mod.Client = MagicMock(side_effect=RuntimeError("no key in test"))
    types_mod = types.ModuleType("google.genai.types")
    types_mod.GenerateContentConfig = MagicMock()
    genai_mod.types = types_mod
    google_pkg.genai = genai_mod
    sys.modules["google.genai"] = genai_mod
    sys.modules["google.genai.types"] = types_mod


_ensure_google_genai_stub()
app_mod = importlib.import_module("app")


class TestEmailHelpers(unittest.TestCase):
    def test_clean_text_normalizes_whitespace(self):
        self.assertEqual(app_mod.clean_text("  hello\r\nworld  "), "hello world")
        self.assertEqual(app_mod.clean_text(""), "")

    def test_decode_mime_header_utf8_and_plain(self):
        self.assertEqual(app_mod.decode_mime_header("Plain Subject"), "Plain Subject")
        encoded = "=?utf-8?b?VGjDtG5nIGLDoW8=?="
        self.assertEqual(app_mod.decode_mime_header(encoded), "Thông báo")
        self.assertEqual(app_mod.decode_mime_header(None), "")

    def test_get_email_body_from_multipart_msg(self):
        msg = EmailMessage()
        msg.set_content("Hello plain body")
        msg.add_alternative("<p>Hello <b>HTML</b></p>", subtype="html")
        raw = email.message_from_bytes(msg.as_bytes())

        text_b, html_b = app_mod.get_email_body_from_msg(raw)
        self.assertIn("Hello plain body", text_b)
        self.assertIn("<b>HTML</b>", html_b)

    def test_get_account_credentials_prefers_matching_then_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_app_file = os.path.join(tmpdir, "app.py")
            accounts_file = os.path.join(tmpdir, "accounts.json")
            with open(accounts_file, "w", encoding="utf-8") as f:
                json.dump(
                    [
                        {"email": "a@gmail.com", "app_password": "pw-a"},
                        {"email": "b@gmail.com", "app_password": "pw-b"},
                    ],
                    f,
                )

            with patch.object(app_mod, "__file__", fake_app_file):
                self.assertEqual(app_mod.get_account_credentials("b@gmail.com"), ("b@gmail.com", "pw-b"))
                self.assertEqual(app_mod.get_account_credentials("other@gmail.com"), ("a@gmail.com", "pw-a"))

        with (
            patch.object(app_mod, "load_accounts", return_value=[]),
            patch.dict(os.environ, {"GMAIL_USER": "env@gmail.com", "GMAIL_APP_PASSWORD": "env-pw"}),
        ):
            self.assertEqual(app_mod.get_account_credentials("default"), ("env@gmail.com", "env-pw"))


class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_api_accounts_returns_env_fallback(self):
        with (
            patch.object(app_mod, "load_accounts", return_value=[]),
            patch.dict(os.environ, {"GMAIL_USER": "demo@gmail.com"}),
        ):
            resp = self.client.get("/api/accounts")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"accounts": ["demo@gmail.com"]})

    def test_api_emails_returns_empty_category_when_no_messages(self):
        with patch.object(app_mod, "get_gmail_emails", return_value=[]):
            resp = self.client.post("/api/emails", json={"days": 1, "account": "default"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"categories": {"Trống": []}})


if __name__ == "__main__":
    unittest.main()
