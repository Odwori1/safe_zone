#!/usr/bin/env python3
"""
Investigate why we see data in some queries but tables show 0 rows
"""
import asyncio
from app.database.database import database

async def investigate_discrepancy():
    """Figure out why we see different data in different contexts"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🔍 INVESTIGATING DATA DISCREPANCY")
        print("================================")
        
        # Check if we're connected to the right database
        db_name = await conn.fetchval('SELECT current_database()')
        print(f"Connected to database: {db_name}")
        
        # Check if there are multiple schemas
        schemas = await conn.fetch('''
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema'
        ''')
        print(f"Available schemas: {[s['schema_name'] for s in schemas]}")
        
        # Check if tables exist in different schemas
        tables = ['user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
        
        for table in tables:
            # Check across all schemas
            table_locations = await conn.fetch('''
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_name = $1
            ''', table)
            
            if table_locations:
                print(f"\n📊 Table '{table}' found in:")
                for loc in table_locations:
                    schema = loc['table_schema']
                    count = await conn.fetchval(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                    print(f"   Schema '{schema}': {count} rows")
            else:
                print(f"\n❌ Table '{table}' not found in any schema")
        
        # Check search_path
        search_path = await conn.fetchval('SHOW search_path')
        print(f"\n🔍 Current search_path: {search_path}")

if __name__ == "__main__":
    asyncio.run(investigate_discrepancy())
