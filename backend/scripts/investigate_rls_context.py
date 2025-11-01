#!/usr/bin/env python3
"""
Investigate the difference between working RLS and crisis RLS
"""

import asyncio
import asyncpg

async def investigate_rls_context():
    print("🔍 Investigating RLS Context Differences...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # Check working tables (posts, comments) RLS policies
    print("\n📊 WORKING TABLES RLS POLICIES:")
    working_tables = ['posts', 'comments', 'journals']
    
    for table in working_tables:
        print(f"\n🔍 Table: {table}")
        policies = await connection.fetch('''
            SELECT policyname, cmd, qual
            FROM pg_policies 
            WHERE tablename = $1
        ''', table)
        
        for policy in policies:
            print(f"   Policy: {policy['policyname']}")
            print(f"     Command: {policy['cmd']}")
            print(f"     Qualifier: {policy['qual']}")
    
    # Check what set_current_user_id function actually does
    print("\n🔧 set_current_user_id FUNCTION ANALYSIS:")
    func_def = await connection.fetchval('''
        SELECT pg_get_functiondef(oid) 
        FROM pg_proc 
        WHERE proname = 'set_current_user_id'
    ''')
    print(f"Function definition: {func_def}")
    
    # Test the difference between the two approaches
    print("\n🧪 TESTING CONTEXT SETTING APPROACHES:")
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    # Test set_current_user_id approach
    print("1. Testing set_current_user_id() approach:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    current_context = await connection.fetchval("SELECT current_setting('app.current_user_id', true)")
    print(f"   Context after set_current_user_id: {current_context}")
    
    # Test direct setting approach (what crisis tables expect)
    print("2. Testing direct SET approach:")
    await connection.execute(f"SET app.current_user_id TO '{test_user_id}'")
    current_context = await connection.fetchval("SELECT current_setting('app.current_user_id', true)")
    print(f"   Context after direct SET: {current_context}")
    
    # Check if there's a difference in how they work
    print("\3. Checking function behavior:")
    func_behavior = await connection.fetchval('''
        SELECT set_config('app.current_user_id', $1::text, false)
    ''', test_user_id)
    print(f"   set_config result: {func_behavior}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(investigate_rls_context())
