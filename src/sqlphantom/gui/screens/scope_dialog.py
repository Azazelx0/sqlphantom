"""
SQLPhantom PySide6 Scope Boundary Configuration Dialog.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.domain.models import ScopeRule, Target
from sqlphantom.domain.scope import validate_target_in_scope


class ScopeConfigDialog(QDialog):
    """
    Visual dialog for inspecting and editing boundary safety scope rules.
    Supports allowed domains, URL patterns, private IP blocking, and
    an interactive pre-flight scope testing workbench.
    """

    def __init__(self, current_scope: ScopeRule | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Scope Boundary Rules & Safety Guardrails")
        self.resize(560, 480)

        self._scope = current_scope or ScopeRule()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_lbl = QLabel("Scope Boundary Safeguards")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel("Enforce strict target domain, CIDR, and private IP boundaries to ensure authorized testing.")
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(desc_lbl)

        # Frame: Configuration
        form_frame = QFrame()
        form_frame.setProperty("class", "card-frame")
        form_layout = QVBoxLayout(form_frame)

        form_layout.addWidget(QLabel("Allowed Domains (one per line or comma-separated):"))
        self.txt_domains = QPlainTextEdit()
        self.txt_domains.setMaximumHeight(80)
        self.txt_domains.setPlainText("\n".join(self._scope.allowed_domains))
        form_layout.addWidget(self.txt_domains)

        form_layout.addWidget(QLabel("Allowed URL Patterns (Regex or Glob, one per line):"))
        self.txt_patterns = QPlainTextEdit()
        self.txt_patterns.setMaximumHeight(60)
        self.txt_patterns.setPlainText("\n".join(self._scope.allowed_url_patterns))
        form_layout.addWidget(self.txt_patterns)

        self.chk_block_private = QCheckBox("Enforce Private IP Blocking (Blocks 127.0.0.1, 10.0.0.0/8, 192.168.0.0/16)")
        self.chk_block_private.setChecked(self._scope.block_private_ips)
        form_layout.addWidget(self.chk_block_private)

        layout.addWidget(form_frame)

        # Pre-Flight Test Box
        test_frame = QFrame()
        test_frame.setProperty("class", "card-frame")
        test_layout = QVBoxLayout(test_frame)
        test_layout.addWidget(QLabel("Pre-Flight Scope Test Workbench:"))

        test_row = QHBoxLayout()
        self.input_test_url = QLineEdit("http://testphp.vulnweb.com/listproducts.php")
        self.input_test_url.setPlaceholderText("Enter test URL...")
        self.btn_test = QPushButton("Test URL")
        self.btn_test.setProperty("class", "secondary")
        self.btn_test.clicked.connect(self._test_url)

        test_row.addWidget(self.input_test_url)
        test_row.addWidget(self.btn_test)
        test_layout.addLayout(test_row)

        self.lbl_test_result = QLabel("")
        self.lbl_test_result.setStyleSheet("font-weight: bold;")
        test_layout.addWidget(self.lbl_test_result)
        layout.addWidget(test_frame)

        # Dialog Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_scope_rule(self) -> ScopeRule:
        """Construct validated ScopeRule from form values."""
        raw_domains = self.txt_domains.toPlainText().replace(",", "\n").split("\n")
        allowed_domains = [d.strip() for d in raw_domains if d.strip()]

        raw_patterns = self.txt_patterns.toPlainText().split("\n")
        patterns = [p.strip() for p in raw_patterns if p.strip()]

        block_private = self.chk_block_private.isChecked()
        return ScopeRule(
            allowed_domains=allowed_domains,
            allowed_url_patterns=patterns,
            block_private_ips=block_private,
        )

    def _test_url(self) -> None:
        url = self.input_test_url.text().strip()
        if not url:
            self.lbl_test_result.setText("Enter a URL to test.")
            return

        scope = self.get_scope_rule()
        target = Target(url=url)
        in_scope, reason = validate_target_in_scope(target, scope)
        if in_scope:
            self.lbl_test_result.setText(f"✅ Target IN SCOPE: Authorized for assessment.")
            self.lbl_test_result.setStyleSheet("color: #10B981; font-weight: bold;")
        else:
            self.lbl_test_result.setText(f"❌ Target REJECTED: {reason}")
            self.lbl_test_result.setStyleSheet("color: #EF4444; font-weight: bold;")
