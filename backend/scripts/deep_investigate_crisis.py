#!/usr/bin/env python3
"""
Deep investigation of crisis system state
"""
import asyncio
from app.database.database import database

async def deep_investigate():
    """Thorough investigation of crisis system"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🔍 DEEP CRISIS SYSTEM INVESTIGATION")
        print("===================================")
        
        # 1. Check database connection details
        db_info = await conn.fetchrow('''
            SELECT current_database(), current_user, inet_client_addr(), version()
        ''')
        print(f"Database: {db_info['current_database']}")
        print(f"User: {db_info['current_user']}")
        print(f"Client: {db_info['inet_client_addr']}")
        print(f"PostgreSQL: {db_info['version'].split(',')[0]}")
        
        # 2. Check ALL tables in the database
        print("\n📋 ALL TABLES IN DATABASE:")
        all_tables = await conn.fetch('''
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        ''')
        for table in all_tables:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table["table_name"]}')
            print(f"  {table['table_name']} ({table['table_type']}): {count} rows")
        
        # 3. Check if we have any users
        print("\n👥 USERS IN DATABASE:")
        users = await conn.fetch('SELECT id, email, username FROM users LIMIT 5')
        for user in users:
            print(f"  {user['email']} ({user['username']}) - {user['id']}")
        
        # 4. Check crisis_resources specifically (since it has data)
        print("\n📞 CRISIS_RESOURCES DATA:")
        resources = await conn.fetch('SELECT id, name, category FROM crisis_resources')
        for resource in resources:
            print(f"  {resource['name']} ({resource['category']}) - {resource['id']}")
        
        # 5. Check if there were recent changes (transaction logs not accessible, but we can check timestamps)
        print("\n⏰ CRISIS TABLES CREATION TIMES:")
        crisis_tables = ['user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
        for table in crisis_tables:
            try:
                # Try to get creation time (this might not work on all setups)
                created = await conn.fetchval(f'''
                    SELECT created FROM pg_stat_all_tables 
                    WHERE relname = '{table}'
                ''')
                if created:
                    print(f"  {table}: {created}")
                else:
                    print(f"  {table}: creation time not available")
            except:
                print(f"  {table}: could not check creation time")

if __name__ == "__main__":
    asyncio.run(deep_investigate())
