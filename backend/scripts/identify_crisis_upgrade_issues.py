#!/usr/bin/env python3
"""
Identify specific upgrade issues in crisis system
"""
import asyncio
from app.database.database import database

async def identify_upgrade_issues():
    """Identify specific schema mismatches causing upgrade issues"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🎯 IDENTIFYING CRISIS UPGRADE ISSUES")
        print("====================================")
        
        # Issue 1: Check safety_plans schema mismatch
        print("\n1. SAFETY_PLANS SCHEMA MISMATCH")
        safety_columns = await conn.fetch('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'safety_plans'
            ORDER BY column_name;
        ''')
        current_columns = [row['column_name'] for row in safety_columns]
        print(f"   Current columns: {current_columns}")
        
        # Expected columns from upgraded system
        expected_columns = ['warning_signs', 'external_coping_strategies', 'reasons_for_living']
        missing_columns = [col for col in expected_columns if col not in current_columns]
        print(f"   Missing columns: {missing_columns}")
        
        # Issue 2: Check crisis_alerts location_data type
        print("\n2. CRISIS_ALERTS LOCATION_DATA TYPE")
        location_type = await conn.fetchval('''
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'crisis_alerts' AND column_name = 'location_data';
        ''')
        print(f"   location_data type: {location_type}")
        print(f"   Expected: jsonb, Actual: {location_type}")
        
        # Issue 3: Check RLS policies
        print("\n3. RLS POLICY CONTEXT")
        policies = await conn.fetch('''
            SELECT tablename, policyname, cmd, qual
            FROM pg_policies 
            WHERE schemaname = 'public'
            AND tablename IN ('user_crisis_preferences', 'emergency_contacts', 'wellness_checkins')
            AND cmd = 'INSERT';
        ''')
        
        for policy in policies:
            print(f"   Table: {policy['tablename']}")
            print(f"     Policy: {policy['policyname']}")
            print(f"     Condition: {policy['qual']}")
        
        # Issue 4: Check if backend is setting user context
        print("\n4. BACKEND USER CONTEXT SETTING")
        print("   RLS policies expect: app.current_user_id")
        print("   Need to verify backend sets this for each request")

if __name__ == "__main__":
    asyncio.run(identify_upgrade_issues())
