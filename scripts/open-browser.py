#!/usr/bin/env python
"""open-browser script opens any file inside of a browser. We will mainly use this to look at unit tests locally"""
# flake8: noqa
import os
import sys
import webbrowser

URL = sys.argv[1]

FINAL_ADDRESS = f"{URL}"

print(f"FINAL_ADDRESS: {FINAL_ADDRESS}")

# MacOS
CHROME_PATH = r"open -a /Applications/Google\ Chrome.app %s"  # pylint: disable=anomalous-backslash-in-string

webbrowser.get(CHROME_PATH).open(FINAL_ADDRESS)
