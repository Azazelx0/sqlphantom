"""
SQLPhantom command line interface entry points.
"""

import argparse
import sys

from sqlphantom import (
    __description__,
    __product__,
    __tagline__,
    __upstream__,
    __upstream_commit__,
    __version__,
)


def banner() -> str:
    return rf"""
   ____  ____  __    ____  _                 _                  
  / ___|/ __ \| |   |  _ \| |__   __ _ _ __ | |_ ___  _ __ ___  
  \___ \ |  | | |   | |_) | '_ \ / _` | '_ \| __/ _ \| '_ ` _ \ 
   ___) | |__| | |___|  __/| | | | (_| | | | | || (_) | | | | | |
  |____/ \___\_\_____|_|   |_| |_|\__,_|_| |_|\__\___/|_| |_| |_|
  
  {__product__} · Enhanced sqlmap (v{__version__})
  {__tagline__}
  Upstream: {__upstream__} ({__upstream_commit__[:7]})
"""


def main(args: list[str] | None = None) -> int:
    """Primary CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="sqlphantom",
        description=f"{__product__} — {__tagline__}\n{__description__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{__product__} v{__version__} (upstream sqlmap {__upstream_commit__[:7]})",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the PySide6 desktop GUI workstation (Phase 3)",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch the Textual interactive terminal UI (Phase 2)",
    )

    parsed = parser.parse_args(args)

    if parsed.gui:
        return gui()
    elif parsed.tui:
        return tui()

    print(banner())
    print("Welcome to SQLPhantom — sqlmap, reimagined.\n")
    print("Status: Phase 1 (Foundation Milestone) is active.")
    print("Available entry points:")
    print("  sqlphantom --help    Display this help overview")
    print("  sqlphantom --tui     Interactive Textual Terminal UI (Phase 2)")
    print("  sqlphantom --gui     Modern PySide6 Desktop GUI (Phase 3)")
    print("\nFor full documentation, see README.md and USAGE.md.")
    return 0


def gui() -> int:
    """Launch the PySide6 desktop graphical interface."""
    print(banner())
    print("[*] Launching SQLPhantom PySide6 Desktop GUI...")
    print("[!] Desktop GUI workstation is under active development (Roadmap Phase 3).")
    print("[*] Core domain, scope enforcement, and engine services are fully operational.")
    return 0


def tui() -> int:
    """Launch the Textual interactive terminal interface."""
    print(banner())
    print("[*] Launching SQLPhantom Textual Interactive Terminal...")
    print("[!] Terminal UI workstation is under active development (Roadmap Phase 2).")
    print("[*] Core domain, scope enforcement, and engine services are fully operational.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
