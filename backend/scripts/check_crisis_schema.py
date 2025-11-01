#!/usr/bin/env python3
"""
Check the exact schema of crisis tables
"""

import asyncio
import asyncpg

async def check_crisis_schema():
    print("🔍 Checking Crisis Table Schema...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    crisis_tables = ['user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
    
    for table in crisis_tables:
        print(f"\n📋 Table: {table}")
        
        # Get column information
        columns = await connection.fetch('''
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position
        ''', table)
        
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(check_crisis_schema())
