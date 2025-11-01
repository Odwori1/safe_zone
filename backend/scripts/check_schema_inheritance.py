#!/usr/bin/env python3
"""
Check the complete schema inheritance chain
"""

# Find all files that might contain TimeStampedSchema
import os
import glob

schema_files = glob.glob("app/schemas/**/*.py", recursive=True)

for file in schema_files:
    with open(file, 'r') as f:
        content = f.read()
        if 'TimeStampedSchema' in content:
            print(f"🔍 Found in: {file}")
            # Look for class definition
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'class TimeStampedSchema' in line:
                    print(f"   Line {i+1}: {line.strip()}")
                    # Print the next 10 lines
                    for j in range(i+1, min(i+11, len(lines))):
                        print(f"   {lines[j]}")
                    break
