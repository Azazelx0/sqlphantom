# Third-Party Notices & Licenses

SQLPhantom incorporates open-source software and builds upon upstream sqlmap. This document provides attribution, copyright notices, and license terms for third-party components included in or utilized by SQLPhantom.

---

## 1. Upstream Engine Attribution: sqlmap

SQLPhantom is an independent, modernized fork built upon the [sqlmap](https://sqlmap.org) project.

- **Project**: sqlmap (automatic SQL injection and database takeover tool)
- **Authors & Original Developers**: Bernardo Damele A. G. and Miroslav Stampar
- **Website**: <https://sqlmap.org>
- **Source Repository**: <https://github.com/sqlmapproject/sqlmap>
- **Pinned Commit Baseline**: [`6e06114947397e1f5bbe428230e25cf1cf9f1a55`](https://github.com/sqlmapproject/sqlmap/commit/6e06114947397e1f5bbe428230e25cf1cf9f1a55) (Release `1.10.10`)
- **License**: GNU General Public License version 2.0 or later (GPL-2.0-or-later)
- **Copyright**: Copyright (c) 2006-2026 sqlmap developers

### Independence Notice
SQLPhantom is an independent project and is **not** an official release of sqlmap, nor is it sponsored, affiliated with, or endorsed by Bernardo Damele A. G., Miroslav Stampar, or the official sqlmap development team. All upstream copyrights, trademarks, and intellectual property remain with their respective holders.

---

## 2. Modified Upstream Files Tracking

To ensure upstream maintainability and cleanly separate SQLPhantom's modernization layer from the core detection engine, SQLPhantom interacts with sqlmap through the official REST API (`sqlmapapi.py`) rather than altering internal detection code.

| File Path in `sqlmap/` | Status | Modification Summary |
| :--- | :--- | :--- |
| *(All files under `sqlmap/`)* | **Pristine (Unmodified)** | No upstream files are modified. Upstream sqlmap is preserved in its original release state at commit `6e06114`. |

Any future upstream modifications (if ever required for compatibility) will be strictly cataloged in this table along with rationale and patch links.

---

## 3. Runtime Dependency Inventory

The following third-party libraries are direct runtime dependencies of SQLPhantom as defined in [`pyproject.toml`](file:///d:/Projects/SQLPhantom/pyproject.toml):

| Package | Version Constraint | License | Project URL / Source |
| :--- | :--- | :--- | :--- |
| **PySide6** | `>=6.6` | LGPL v3 / Commercial | <https://wiki.qt.io/Qt_for_Python> |
| **textual** | `>=0.40` | MIT License | <https://github.com/Textualize/textual> |
| **pydantic** | `>=2.0` | MIT License | <https://github.com/pydantic/pydantic> |
| **rich** | `>=13.0` | MIT License | <https://github.com/Textualize/rich> |
| **httpx** | `>=0.25` | BSD 3-Clause License | <https://github.com/encode/httpx> |

---

## 4. Development & Build Dependency Inventory

The following tools are used during development, linting, type-checking, testing, and packaging:

| Package | Version Constraint | License | Project URL / Source |
| :--- | :--- | :--- | :--- |
| **hatchling** | *(build-system)* | MIT License | <https://github.com/pypa/hatch> |
| **pytest** | `>=8.0` | MIT License | <https://github.com/pytest-dev/pytest> |
| **pytest-asyncio** | `>=0.23` | Apache License 2.0 | <https://github.com/pytest-dev/pytest-asyncio> |
| **pytest-qt** | `>=4.2` | MIT License | <https://github.com/pytest-dev/pytest-qt> |
| **ruff** | `>=0.4` | MIT / Apache 2.0 | <https://github.com/astral-sh/ruff> |
| **mypy** | `>=1.10` | MIT License | <https://github.com/python/mypy> |

---

## 5. License Texts

### 5.1. GNU General Public License Version 2 (GPL-2.0)
*(Applies to SQLPhantom and upstream sqlmap)*

```
GNU GENERAL PUBLIC LICENSE
Version 2, June 1991

Copyright (C) 1989, 1991 Free Software Foundation, Inc.
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.

Preamble

The licenses for most software are designed to take away your
freedom to share and change it.  By contrast, the GNU General Public
License is intended to guarantee your freedom to share and change free
software--to make sure the software is free for all its users.  This
General Public License applies to most of the Free Software
Foundation's software and to any other program whose authors commit to
using it.  (Some other Free Software Foundation software is covered by
the GNU Library General Public License instead.)  You can apply it to
your programs, too.

When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
this service if you wish), that you receive source code or can get it
if you want it, that you can change the software or use pieces of it
in new free programs; and that you know you can do these things.

[For the complete terms and conditions of GNU General Public License Version 2,
visit: https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt]
```

### 5.2. MIT License
*(Applies to textual, pydantic, rich, pytest, pytest-qt, mypy, hatchling)*

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 5.3. BSD 3-Clause License
*(Applies to httpx)*

```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

### 5.4. GNU Lesser General Public License Version 3 (LGPL-3.0)
*(Applies to PySide6)*

PySide6 is licensed under the GNU Lesser General Public License version 3.0 (LGPL-3.0) as published by the Free Software Foundation. A copy of the LGPL-3.0 license is available at <https://www.gnu.org/licenses/lgpl-3.0.html>. In compliance with the LGPL, users may dynamically link alternative builds of Qt/PySide6.
