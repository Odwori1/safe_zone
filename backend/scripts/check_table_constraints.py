#!/usr/bin/env python3
"""
Check table constraints to understand the primary key
"""

import asyncio
import asyncpg

async def check_constraints():
    print("🔍 Checking user_crisis_preferences table constraints...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # Check primary key
    pk_info = await connection.fetch('''
        SELECT 
            tc.constraint_name,
            kcu.column_name,
            tc.constraint_type
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'user_crisis_preferences'
        AND tc.constraint_type = 'PRIMARY KEY'
    ''')
    
    print("Primary Key Information:")
    for row in pk_info:
        print(f"   Constraint: {row['constraint_name']}")
        print(f"   Column: {row['column_name']}")
        print(f"   Type: {row['constraint_type']}")
    
    # Check unique constraints
    unique_info = await connection.fetch('''
        SELECT 
            tc.constraint_name,
            kcu.column_name,
            tc.constraint_type
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'user_crisis_preferences'
        AND tc.constraint_type = 'UNIQUE'
    ''')
    
    if unique_info:
        print("\nUnique Constraints:")
        for row in unique_info:
            print(f"   Constraint: {row['constraint_name']}")
            print(f"   Column: {row['column_name']}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(check_constraints())
