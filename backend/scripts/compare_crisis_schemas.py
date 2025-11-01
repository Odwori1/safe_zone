#!/usr/bin/env python3
"""
Compare original vs upgraded crisis schemas to identify issues
"""
import asyncio
from app.database.database import database

async def compare_crisis_schemas():
    """Compare what's in database vs what the upgraded system expects"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🔍 COMPARING CRISIS SCHEMAS")
        print("===========================")
        
        # Check current table structures
        tables = [
            'user_crisis_preferences',
            'emergency_contacts', 
            'safety_plans',
            'wellness_checkins',
            'crisis_alerts',
            'crisis_resources'
        ]
        
        for table in tables:
            print(f"\n📊 TABLE: {table}")
            print("-" * 40)
            
            # Get current columns
            columns = await conn.fetch('''
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = $1
                ORDER BY ordinal_position;
            ''', table)
            
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"  {col['column_name']}: {col['data_type']} {nullable} {default}")
            
            # Check row count
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table}')
            print(f"  Rows: {count}")

if __name__ == "__main__":
    asyncio.run(compare_crisis_schemas())
