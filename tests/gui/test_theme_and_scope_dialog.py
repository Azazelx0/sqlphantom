"""
Automated tests for Light/Dark Theme switching and ScopeConfigDialog.
"""

from sqlphantom.domain.models import ScopeRule
from sqlphantom.gui.main_window import MainWindow
from sqlphantom.gui.screens.scope_dialog import ScopeConfigDialog
from sqlphantom.gui.theme import DARK_STYLESHEET, LIGHT_STYLESHEET, get_theme_stylesheet


def test_theme_stylesheets():
    assert "0B0F19" in DARK_STYLESHEET
    assert "F8FAFC" in LIGHT_STYLESHEET
    assert get_theme_stylesheet("dark") == DARK_STYLESHEET
    assert get_theme_stylesheet("light") == LIGHT_STYLESHEET


def test_main_window_theme_toggle(qtbot):
    window = MainWindow(db_path=":memory:")
    qtbot.addWidget(window)

    assert window.current_theme == "dark"
    window.toggle_theme()
    assert window.current_theme == "light"
    window.toggle_theme()
    assert window.current_theme == "dark"


def test_scope_dialog_rule_construction(qtbot):
    init_scope = ScopeRule(allowed_domains=["example.com"], block_private_ips=True)
    dialog = ScopeConfigDialog(init_scope)
    qtbot.addWidget(dialog)

    # Edit inputs
    dialog.txt_domains.setPlainText("target.org\napi.target.org")
    dialog.txt_patterns.setPlainText("^https://target\\.org/api/.*$")
    dialog.chk_block_private.setChecked(False)

    built_scope = dialog.get_scope_rule()
    assert built_scope.allowed_domains == ["target.org", "api.target.org"]
    assert built_scope.allowed_url_patterns == ["^https://target\\.org/api/.*$"]
    assert built_scope.block_private_ips is False


def test_scope_dialog_preflight_testing(qtbot):
    init_scope = ScopeRule(allowed_domains=["vulnweb.com"], block_private_ips=True)
    dialog = ScopeConfigDialog(init_scope)
    qtbot.addWidget(dialog)

    # Test allowed target
    dialog.input_test_url.setText("http://testphp.vulnweb.com/listproducts.php")
    dialog._test_url()
    assert "IN SCOPE" in dialog.lbl_test_result.text()

    # Test disallowed target
    dialog.input_test_url.setText("http://evil-third-party.com/test")
    dialog._test_url()
    assert "REJECTED" in dialog.lbl_test_result.text()
