"""
SQLPhantom PySide6 Raw HTTP Request Editor screen.
"""

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.domain.enums import HttpMethod
from sqlphantom.domain.models import Target


class RequestEditorScreen(QWidget):
    """
    Raw HTTP Request Workbench enabling manual request crafting,
    Burp Suite / OWASP ZAP request import, and parameter extraction.
    """

    SAMPLE_REQUEST = (
        "POST /api/v1/auth/login HTTP/1.1\n"
        "Host: testphp.vulnweb.com\n"
        "User-Agent: Mozilla/5.0 (Security Tester; SQLPhantom)\n"
        "Content-Type: application/json\n"
        "Accept: application/json\n"
        "Cookie: session_id=7a8b9c0d1e2f3a4b\n\n"
        '{"username": "admin\' OR 1=1 --", "password": "password123"}'
    )

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_lbl = QLabel("Raw HTTP Request Workbench")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        sub_lbl = QLabel("Import, paste, or craft raw HTTP requests from Burp Suite / OWASP ZAP.")
        sub_lbl.setStyleSheet("font-size: 13px; color: #94A3B8;")
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)

        card = QFrame()
        card.setProperty("class", "card-frame")
        card_layout = QVBoxLayout(card)

        self.editor = QPlainTextEdit(self.SAMPLE_REQUEST)
        self.editor.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #050811;
                border: 1px solid #334155;
                color: #38BDF8;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            """
        )
        card_layout.addWidget(self.editor)

        self.lbl_parsed = QLabel("")
        self.lbl_parsed.setStyleSheet("color: #A855F7; font-weight: bold;")
        card_layout.addWidget(self.lbl_parsed)

        btn_row = QHBoxLayout()
        self.btn_parse = QPushButton("Parse & Validate Request")
        self.btn_send_wizard = QPushButton("Transfer to Assessment Wizard")
        self.btn_send_wizard.setProperty("class", "secondary")

        self.btn_parse.clicked.connect(self.parse_request)
        self.btn_send_wizard.clicked.connect(self.transfer_to_wizard)

        btn_row.addWidget(self.btn_parse)
        btn_row.addWidget(self.btn_send_wizard)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        layout.addWidget(card)

    def parse_request(self) -> Target | None:
        raw = self.editor.toPlainText().strip()
        if not raw:
            self.lbl_parsed.setText("Error: Empty request content")
            return None

        lines = raw.splitlines()
        first_line = lines[0].strip().split()
        if len(first_line) < 2:
            self.lbl_parsed.setText("Error: Malformed request line (expected METHOD PATH)")
            return None

        method_str = first_line[0].upper()
        path = first_line[1]

        headers: dict[str, str] = {}
        cookies: dict[str, str] = {}
        host = ""
        body_start = -1

        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                body_start = i + 1
                break
            if ":" in line:
                k, v = line.split(":", 1)
                k_clean = k.strip()
                v_clean = v.strip()
                if k_clean.lower() == "host":
                    host = v_clean
                elif k_clean.lower() == "cookie":
                    for cookie_pair in v_clean.split(";"):
                        if "=" in cookie_pair:
                            ck, cv = cookie_pair.strip().split("=", 1)
                            cookies[ck] = cv
                else:
                    headers[k_clean] = v_clean

        body = None
        if body_start != -1 and body_start < len(lines):
            body = "\n".join(lines[body_start:])

        scheme = "https" if "443" in host else "http"
        full_url = f"{scheme}://{host or 'localhost'}{path}"

        try:
            method = HttpMethod(method_str)
        except ValueError:
            method = HttpMethod.GET

        target = Target(url=full_url, method=method, headers=headers, cookies=cookies, data=body)
        self.lbl_parsed.setText(
            f"Successfully parsed: {target.method} {target.url} ({len(headers)} headers, {len(cookies)} cookies)"
        )
        return target

    def transfer_to_wizard(self) -> None:
        target = self.parse_request()
        if target:
            wizard = self.main_window.screens.get("wizard")
            if wizard:
                wizard.input_url.setText(target.url)
                wizard.combo_method.setCurrentText(str(target.method))
            self.main_window.navigate_to("wizard")
