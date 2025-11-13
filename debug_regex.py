#!/usr/bin/env python3
"""Debug figure block detection."""

import re

def test_regex():
    """Test the regex for figure block detection."""
    test_lines = [
        "::: {#fig-CS layout-ncol=\"2\" layout-nrow=\"1\"}",
        "   ::: {#fig-single}",
        "::: {#fig-multi layout-ncol=\"3\"}",
        "regular text",
        ":::"
    ]
    
    pattern = r'^\s*:::\s*\{[^}]*#fig-[^}]*\}'
    
    print("Testing figure block detection regex:")
    for line in test_lines:
        match = bool(re.match(pattern, line.strip()))
        print(f"'{line}' -> {match}")

if __name__ == "__main__":
    test_regex()