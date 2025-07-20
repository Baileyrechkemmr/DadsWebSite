#!/usr/bin/env python3
"""
Fix emoji unicode escapes in the populate_s3_paths.py file
"""

import re

def fix_emojis(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Fix emoji patterns
    content = content.replace('ud83d', '\ud83d')
    content = content.replace('ud83c', '\ud83c')
    content = content.replace('u274c', '\u274c')
    content = content.replace('u2705', '\u2705')
    content = content.replace('u26a0', '\u26a0')
    content = content.replace('u2022', '\u2022')
    content = content.replace('u2728', '\u2728')
    content = content.replace('ufe0f', '\ufe0f')
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Updated {filename} with fixed emoji escapes")

if __name__ == "__main__":
    fix_emojis("populate_s3_paths.py")