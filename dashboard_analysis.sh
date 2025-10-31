#!/bin/bash

echo "🔍 DASHBOARD STRUCTURE ANALYSIS"
echo "================================"

echo ""
echo "1. 📊 CURRENT DASHBOARD PAGE:"
echo "-----------------------------"
DASHBOARD_LINES=$(wc -l < ~/safe_zone/frontend/src/app/dashboard/page.tsx)
echo "   Lines: $DASHBOARD_LINES"
echo "   Content preview:"
head -10 ~/safe_zone/frontend/src/app/dashboard/page.tsx

echo ""
echo "2. 🧩 EXISTING COMPONENT PATTERNS:"
echo "---------------------------------"
echo "   Posts components:"
ls ~/safe_zone/frontend/src/components/posts/ 2>/dev/null | head -5
echo ""
echo "   Journals components:"
ls ~/safe_zone/frontend/src/components/journals/ 2>/dev/null | head -5

echo ""
echo "3. 📱 UI COMPONENTS AVAILABLE:"
echo "-----------------------------"
ls ~/safe_zone/frontend/src/components/ui/ 2>/dev/null | head -10

echo ""
echo "4. 🔗 NAVIGATION STRUCTURE:"
echo "--------------------------"
grep -r "Link" ~/safe_zone/frontend/src/app/dashboard/ --include="*.tsx" --include="*.ts" | head -5

echo ""
echo "5. 🎨 STYLING PATTERNS:"
echo "----------------------"
echo "   Tailwind usage in dashboard:"
grep -o "className=\"[^\"]*\"" ~/safe_zone/frontend/src/app/dashboard/page.tsx 2>/dev/null | head -3

echo ""
echo "========================================"
