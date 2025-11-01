#!/usr/bin/env python3
"""
Check the exact difference in RLS policy creation between working and crisis tables
"""

import asyncio
import asyncpg

async def check_rls_policy_difference():
    print("🔍 Checking RLS Policy Creation Difference...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # The key difference: WITH CHECK vs USING in RLS policies
    print("📊 RLS POLICY STRUCTURE COMPARISON:")
    
    # Check posts table (working) - uses USING only
    posts_policies = await connection.fetch('''
        SELECT policyname, cmd, qual, with_check
        FROM pg_policies 
        WHERE tablename = 'posts'
    ''')
    
    print("Posts table policies (WORKING):")
    for policy in posts_policies:
        print(f"  - {policy['policyname']}:")
        print(f"    USING: {policy['qual']}")
        print(f"    WITH CHECK: {policy['with_check']}")
    
    # Check crisis tables (broken) - use WITH CHECK
    crisis_policies = await connection.fetch('''
        SELECT tablename, policyname, cmd, qual, with_check
        FROM pg_policies 
        WHERE tablename IN ('user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins')
        AND with_check IS NOT NULL
    ''')
    
    print("\nCrisis table policies (BROKEN - have WITH CHECK):")
    for policy in crisis_policies:
        print(f"  - {policy['tablename']}.{policy['policyname']}:")
        print(f"    USING: {policy['qual']}")
        print(f"    WITH CHECK: {policy['with_check']}")
    
    # The critical finding: 
    print("\n🔎 CRITICAL FINDING:")
    print("Working tables use: current_setting('app.current_user_id'::text)::uuid")
    print("Crisis tables use: current_setting('app.current_user_id'::text, true)::uuid")
    print("The 'true' parameter makes it strict - it requires the setting to exist")
    
    # Test what happens with strict vs non-strict
    print("\n🧪 Testing strict vs non-strict current_setting:")
    
    # Clear context first
    await connection.execute("RESET app.current_user_id;")
    
    # Test non-strict (working tables)
    try:
        result = await connection.fetchval("SELECT current_setting('app.current_user_id')::uuid")
        print(f"Non-strict (no 'true'): {result}")
    except Exception as e:
        print(f"Non-strict failed: {e}")
    
    # Test strict (crisis tables) 
    try:
        result = await connection.fetchval("SELECT current_setting('app.current_user_id', true)::uuid")
        print(f"Strict (with 'true'): {result}")
    except Exception as e:
        print(f"Strict failed: {e}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(check_rls_policy_difference())
