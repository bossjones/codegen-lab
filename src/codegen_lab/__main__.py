#!/usr/bin/env python
"""codegen_lab.main."""

from __future__ import annotations

import logging

from codegen_lab.cli import main

rootlogger = logging.getLogger()
handler_logger = logging.getLogger("handler")

name_logger = logging.getLogger(__name__)
logging.getLogger("asyncio").setLevel(logging.DEBUG)  # type: ignore


main()
