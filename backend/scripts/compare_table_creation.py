#!/usr/bin/env python3
"""
Compare how crisis tables vs working tables handle RLS
"""

import asyncio
import asyncpg

async def compare_table_creation():
    print("🔍 Comparing Table Creation Patterns...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # Check the RLS policy details more carefully
    print("📊 RLS POLICY COMPARISON:")
    
    tables_to_compare = ['posts', 'user_crisis_preferences']
    
    for table in tables_to_compare:
        print(f"\n🔍 Table: {table}")
        
        # Get detailed policy information
        policies = await connection.fetch('''
            SELECT policyname, permissive, roles, cmd, qual, with_check
            FROM pg_policies 
            WHERE tablename = $1
        ''', table)
        
        for policy in policies:
            print(f"   Policy: {policy['policyname']}")
            print(f"     Command: {policy['cmd']}")
            print(f"     Using Qualifier: {policy['qual']}")
            print(f"     With Check: {policy['with_check']}")
            print(f"     Permissive: {policy['permissive']}")
            print(f"     Roles: {policy['roles']}")
    
    # Check if there's a pattern in the 'true' parameter
    print("\n🔧 Analyzing current_setting usage:")
    
    crisis_policies = await connection.fetch('''
        SELECT qual 
        FROM pg_policies 
        WHERE qual LIKE '%current_setting%' 
        AND tablename LIKE '%crisis%'
    ''')
    
    working_policies = await connection.fetch('''
        SELECT qual 
        FROM pg_policies 
        WHERE qual LIKE '%current_setting%' 
        AND tablename IN ('posts', 'comments', 'journals')
    ''')
    
    print("Crisis policies current_setting usage:")
    for policy in crisis_policies:
        print(f"  - {policy['qual']}")
    
    print("\nWorking policies current_setting usage:")
    for policy in working_policies:
        print(f"  - {policy['qual']}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(compare_table_creation())
