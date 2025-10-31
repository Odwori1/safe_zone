#!/usr/bin/env python3
"""
Debug script to identify the exact mood schema issue
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.schemas.mood_taxonomy import get_mood_category, get_mood_insights, MoodCategory
    
    print("🔍 Testing mood taxonomy functions:")
    print("===================================")
    
    # Test what get_mood_category returns
    test_moods = ["calm", "anxious", "happy", "sad"]
    for mood in test_moods:
        category = get_mood_category(mood)
        insights = get_mood_insights(mood)
        print(f"Mood: '{mood}'")
        print(f"  Category type: {type(category)}")
        print(f"  Category value: {category}")
        print(f"  Insights type: {type(insights)}")
        print(f"  Insights keys: {list(insights.keys()) if insights else 'None'}")
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
