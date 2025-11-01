import asyncpg
import asyncio

async def check_table_owner():
    try:
        # Connect as the app user first to check owner
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("🔍 Checking crisis_resources table owner...")
        
        owner = await conn.fetchval('''
            SELECT tableowner 
            FROM pg_tables 
            WHERE tablename = 'crisis_resources'
        ''')
        
        print(f"Table owner: {owner}")
        
        await conn.close()
        
        # If owner is different, we might need to connect as that user
        return owner
        
    except Exception as e:
        print(f"Error: {e}")
        return None

asyncio.run(check_table_owner())
