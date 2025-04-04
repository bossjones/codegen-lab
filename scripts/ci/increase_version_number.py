# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""A little helpful script to increment the package version after every release."""

# Enable Python 3's type annotation features
from __future__ import annotations

import importlib.resources  # For accessing package resources
import logging  # For logging functionality
import logging.config  # For configuring logging
import os  # For operating system dependent functionality

# Import required standard library modules
import pathlib  # For working with file paths
import platform  # For getting system information
import re  # For regular expression operations
import string  # For string operations
import sys  # For accessing command line arguments and Python path
import typing  # For type hints
import warnings  # For warning management

import typing_extensions  # For advanced type hints

# Add the current working directory to Python's path to allow importing local packages
sys.path.append(str(pathlib.Path.cwd()))

# Import the version from our package
from codegen_lab import __version__

# Define a regex pattern to match version strings like "1.2.3", "1.2.3.dev4", etc.
# Groups: (major).(minor).(patch)(prerelease type)(prerelease number)
_VERSION_REGEX: typing.Final[typing.Pattern[str]] = re.compile(r"^(\d+)\.(\d+)\.(\d+)(\.[a-z]+)?(\d+)?$", re.IGNORECASE)


class PromptLibraryVersion:
    """Prompt Library version class for handling version numbers and comparisons."""

    # Define class attributes that can be accessed
    __slots__: typing.Sequence[str] = ("_cmp", "prerelease", "version")

    # Type hints for instance attributes
    version: tuple[int, int, int]  # Stores (major, minor, patch) version numbers
    prerelease: tuple[str, int] | None  # Stores prerelease info like (".dev", 0) or None

    def __init__(self, vstring: str) -> None:
        """Initialize version object from version string."""
        # Try to match the version string against our regex pattern
        match = _VERSION_REGEX.match(vstring)
        if not match:
            msg = f"Invalid version: '{vstring}'"
            raise ValueError(msg)

        # Extract version components from regex match
        (major, minor, patch, prerelease, prerelease_num) = match.group(1, 2, 3, 4, 5)

        # Store version tuple (major, minor, patch)
        self.version = (int(major), int(minor), int(patch))
        # Store prerelease info if present, otherwise None
        self.prerelease = (prerelease, int(prerelease_num) if prerelease_num else 0) if prerelease else None

        # Create comparison tuple - uses infinity for releases without prerelease number
        prerelease_num = int(prerelease_num) if prerelease else float("inf")
        self._cmp = (*self.version, prerelease_num)

    def __lt__(self, other: object) -> bool:
        """Check if this version is less than other version."""
        if not isinstance(other, PromptLibraryVersion):
            return NotImplemented

        return self._cmp < other._cmp

    def __le__(self, other: object) -> bool:
        """Check if this version is less than or equal to other version."""
        if not isinstance(other, PromptLibraryVersion):
            return NotImplemented

        return self._cmp <= other._cmp

    @typing_extensions.override
    def __eq__(self, other: object) -> bool:
        """Check if two versions are equal."""
        if not isinstance(other, PromptLibraryVersion):
            return NotImplemented

        return self._cmp == other._cmp

    @typing_extensions.override
    def __ne__(self, other: object) -> bool:
        """Check if two versions are not equal."""
        if not isinstance(other, PromptLibraryVersion):
            return NotImplemented

        return self._cmp != other._cmp

    def __gt__(self, other: object) -> bool:
        """Check if this version is greater than other version."""
        if not isinstance(other, PromptLibraryVersion):
            return NotImplemented

        return self._cmp > other._cmp

    def __ge__(self, other: object) -> bool:
        """Check if this version is greater than or equal to other version."""
        if not isinstance(other, PromptLibraryVersion):
            return NotImplemented

        return self._cmp >= other._cmp

    @typing_extensions.override
    def __repr__(self) -> str:
        """Return string representation of version object."""
        return f"PromptLibraryVersion('{self!s}')"

    @typing_extensions.override
    def __str__(self) -> str:
        """Convert version object to string."""
        # Join version numbers with dots
        vstring = ".".join(map(str, self.version))

        # Add prerelease info if present
        if self.prerelease:
            vstring += "".join(map(str, self.prerelease))

        return vstring

# Create version object from command line argument
version = PromptLibraryVersion(sys.argv[1])

if version.prerelease is not None:
    # If version has prerelease info, increment the prerelease number
    prerelease_str, prerelease_num = version.prerelease
    version.prerelease = (prerelease_str, prerelease_num + 1)

else:
    # If version has no prerelease info:
    # 1. Extract current version numbers
    # 2. Increment patch version
    # 3. Add dev prerelease starting at 0
    major, minor, patch = version.version
    version.version = (major, minor, patch + 1)
    version.prerelease = (".dev", 0)

# Print the new version string
print(version)
