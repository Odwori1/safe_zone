#!/usr/bin/env python3
"""
Diagnose ONLY crisis tables and their RLS policies
"""

import asyncio
import asyncpg
import sys
import os

async def diagnose_crisis_tables():
    print("🔍 Diagnosing CRISIS TABLES RLS Configuration...")
    
    try:
        connection = await asyncpg.connect(
            user="safe_zone_app_user",
            password="secure_app_password_2024",
            database="safe_zone",
            host="localhost",
            port=5433
        )
        
        # Check ALL crisis tables
        crisis_tables = await connection.fetch('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND (table_name LIKE '%crisis%' 
                 OR table_name LIKE '%emergency%' 
                 OR table_name LIKE '%safety%'
                 OR table_name LIKE '%wellness%')
            ORDER BY table_name
        ''')
        
        print("📊 CRISIS TABLES found:")
        for table in crisis_tables:
            print(f"   - {table['table_name']}")
            
            # Check RLS status for each crisis table
            rls_status = await connection.fetchval('''
                SELECT relrowsecurity 
                FROM pg_class 
                WHERE relname = $1
            ''', table['table_name'])
            
            print(f"     RLS Enabled: {rls_status}")
            
            # Check RLS policies for this table
            policies = await connection.fetch('''
                SELECT policyname, permissive, roles, cmd, qual
                FROM pg_policies 
                WHERE tablename = $1
            ''', table['table_name'])
            
            for policy in policies:
                print(f"     Policy: {policy['policyname']}")
                print(f"       Command: {policy['cmd']}")
                print(f"       Qualifier: {policy['qual']}")
        
        print("\n🔐 Checking RLS function requirements...")
        
        # Check if the set_current_user_id function exists
        function_exists = await connection.fetchval('''
            SELECT EXISTS(
                SELECT 1 FROM pg_proc 
                WHERE proname = 'set_current_user_id'
            )
        ''')
        
        print(f"✅ set_current_user_id function exists: {function_exists}")
        
        if function_exists:
            # Check function definition
            func_def = await connection.fetchval('''
                SELECT pg_get_functiondef(oid) 
                FROM pg_proc 
                WHERE proname = 'set_current_user_id'
            ''')
            print(f"📋 Function definition: {func_def}")
        
        await connection.close()
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_crisis_tables())
