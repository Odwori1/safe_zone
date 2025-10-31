#!/bin/bash

echo "🔍 FRONTEND MOOD TRACKING STATUS REPORT"
echo "========================================"

echo ""
echo "1. 📁 EXISTING MOOD FILES:"
echo "--------------------------"
find ~/safe_zone/frontend -name "*mood*" -type f | while read file; do
    echo "   📄 $file"
    echo "   Size: $(wc -l < "$file") lines"
done

echo ""
echo "2. 🗂️ STORES DIRECTORY:"
echo "----------------------"
ls -la ~/safe_zone/frontend/src/stores/ | grep -v "^total"

echo ""
echo "3. 📋 TYPES DIRECTORY:"
echo "---------------------"
ls -la ~/safe_zone/frontend/src/types/ | grep -v "^total"

echo ""
echo "4. 🧩 COMPONENTS STRUCTURE:"
echo "--------------------------"
ls -la ~/safe_zone/frontend/src/components/ | head -10

echo ""
echo "5. 📊 DASHBOARD STRUCTURE:"
echo "-------------------------"
ls -la ~/safe_zone/frontend/src/app/dashboard/

echo ""
echo "6. 📦 CHART DEPENDENCIES:"
echo "------------------------"
grep -E "(chart|recharts|victory|vis|apex)" ~/safe_zone/frontend/package.json || echo "   No chart libraries found"

echo ""
echo "========================================"
