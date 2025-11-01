import asyncpg
import asyncio

async def check_table_structure():
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        # Check crisis_resources table structure
        print("🔍 Checking crisis_resources table structure...")
        result = await conn.fetchrow("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'crisis_resources'
            ORDER BY ordinal_position;
        """)
        
        print("Table structure:")
        for row in await conn.fetch("SELECT * FROM crisis_resources LIMIT 1"):
            print("\nSample row:")
            for key, value in row.items():
                print(f"  {key}: {value} (type: {type(value)})")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_table_structure())
