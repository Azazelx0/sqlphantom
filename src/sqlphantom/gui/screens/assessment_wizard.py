"""
SQLPhantom PySide6 Assessment Setup Wizard screen.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.domain.enums import HttpMethod
from sqlphantom.domain.models import AssessmentConfig, ScopeRule, Target
from sqlphantom.domain.scope import validate_target_in_scope


class AssessmentWizardScreen(QWidget):
    """
    Form-based wizard for configuring targets, boundary scopes, and injection parameters.
    """

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_lbl = QLabel("New Security Assessment Configuration")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        sub_lbl = QLabel("Configure target parameters, scope guardrails, and injection levels.")
        sub_lbl.setStyleSheet("font-size: 13px; color: #94A3B8;")
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)

        form_frame = QFrame()
        form_frame.setProperty("class", "card-frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)

        # Target URL
        form_layout.addWidget(QLabel("Target URL (HTTP/HTTPS):"))
        self.input_url = QLineEdit("http://testphp.vulnweb.com/listproducts.php?cat=1")
        self.input_url.setPlaceholderText("http://example.com/item.php?id=1")
        form_layout.addWidget(self.input_url)

        # Method & Scope
        row1 = QHBoxLayout()
        v_method = QVBoxLayout()
        v_method.addWidget(QLabel("HTTP Method:"))
        self.combo_method = QComboBox()
        self.combo_method.addItems(["GET", "POST", "PUT", "DELETE", "PATCH"])
        v_method.addWidget(self.combo_method)
        row1.addLayout(v_method)

        v_scope = QVBoxLayout()
        v_scope.addWidget(QLabel("Allowed Domains Scope (comma-separated):"))
        self.input_domains = QLineEdit("vulnweb.com")
        self.input_domains.setPlaceholderText("example.com, api.internal")
        v_scope.addWidget(self.input_domains)
        row1.addLayout(v_scope)
        form_layout.addLayout(row1)

        # Level & Risk
        row2 = QHBoxLayout()
        v_level = QVBoxLayout()
        v_level.addWidget(QLabel("Testing Level (1-5):"))
        self.spin_level = QSpinBox()
        self.spin_level.setRange(1, 5)
        self.spin_level.setValue(2)
        v_level.addWidget(self.spin_level)
        row2.addLayout(v_level)

        v_risk = QVBoxLayout()
        v_risk.addWidget(QLabel("Risk Vector (1-3):"))
        self.spin_risk = QSpinBox()
        self.spin_risk.setRange(1, 3)
        self.spin_risk.setValue(1)
        v_risk.addWidget(self.spin_risk)
        row2.addLayout(v_risk)
        form_layout.addLayout(row2)

        # Network Tuning: Proxy & Delay
        row3 = QHBoxLayout()
        v_proxy = QVBoxLayout()
        v_proxy.addWidget(QLabel("Upstream Proxy (e.g. http://127.0.0.1:8080):"))
        self.input_proxy = QLineEdit()
        self.input_proxy.setPlaceholderText("Optional: http://proxy:port or socks5://127.0.0.1:9050")
        v_proxy.addWidget(self.input_proxy)
        row3.addLayout(v_proxy)

        v_delay = QVBoxLayout()
        v_delay.addWidget(QLabel("Request Delay / Throttle (sec):"))
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.0, 10.0)
        self.spin_delay.setSingleStep(0.25)
        self.spin_delay.setValue(0.0)
        v_delay.addWidget(self.spin_delay)
        row3.addLayout(v_delay)
        form_layout.addLayout(row3)

        # Boundary Safeguard Checkbox
        self.chk_private_ips = QCheckBox("Block RFC 1918 / Loopback Private IP addresses (Recommended)")
        self.chk_private_ips.setChecked(True)
        form_layout.addWidget(self.chk_private_ips)

        # Error / Validation Label
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #EF4444; font-weight: bold;")
        form_layout.addWidget(self.lbl_error)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_launch = QPushButton("Launch Assessment")
        self.btn_cancel = QPushButton("Cancel / Back")
        self.btn_cancel.setProperty("class", "secondary")

        self.btn_launch.clicked.connect(self.launch_assessment)
        self.btn_cancel.clicked.connect(lambda: self.main_window.navigate_to("dashboard"))

        btn_layout.addWidget(self.btn_launch)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)

        layout.addWidget(form_frame)
        layout.addStretch()

    def launch_assessment(self) -> None:
        self.lbl_error.setText("")
        url = self.input_url.text().strip()
        method_str = self.combo_method.currentText()
        domains_str = self.input_domains.text().strip()
        level = self.spin_level.value()
        risk = self.spin_risk.value()
        block_private = self.chk_private_ips.isChecked()

        if not url:
            self.lbl_error.setText("Error: Target URL cannot be empty")
            return

        method = HttpMethod(method_str)
        allowed_domains = [d.strip() for d in domains_str.split(",") if d.strip()]
        scope = ScopeRule(allowed_domains=allowed_domains, block_private_ips=block_private)
        target = Target(url=url, method=method)

        in_scope, reason = validate_target_in_scope(target, scope)
        if not in_scope:
            self.lbl_error.setText(f"Scope Rejected: {reason}")
            return

        proxy_val = self.input_proxy.text().strip() or None
        delay_val = self.spin_delay.value()

        config = AssessmentConfig(
            target=target,
            scope=scope,
            level=level,
            risk=risk,
            proxy=proxy_val,
            delay=delay_val,
        )

        try:
            job_id = self.main_window.assessment_service.create_assessment(config)
            self.main_window.assessment_service.start_assessment(job_id)
            self.main_window.active_job_id = job_id
            self.main_window.navigate_to("monitor")
        except Exception as exc:
            self.lbl_error.setText(f"Execution Error: {exc}")
