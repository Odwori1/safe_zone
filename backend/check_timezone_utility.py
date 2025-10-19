#!/usr/bin/env python3
"""
Check what's available in the timezone utility
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.utils.timezone import timezone_handler

print("🔍 CHECKING TIMEZONE UTILITY")
print("=" * 50)

print(f"Timezone handler type: {type(timezone_handler)}")
print(f"Timezone handler attributes: {dir(timezone_handler)}")

# Check if it has the expected methods
if hasattr(timezone_handler, 'convert_to_user_tz'):
    print("✅ convert_to_user_tz method exists")
else:
    print("❌ convert_to_user_tz method not found")

if hasattr(timezone_handler, 'get_user_timezone'):
    print("✅ get_user_timezone method exists")
else:
    print("❌ get_user_timezone method not found")

# Let's see what methods are available
available_methods = [method for method in dir(timezone_handler) if not method.startswith('_')]
print(f"Available methods: {available_methods}")
