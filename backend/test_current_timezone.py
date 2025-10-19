import asyncio
from app.database.database import database
from datetime import datetime, timezone as tz  # Rename import to avoid conflict

async def test_current_timezone():
    print("🌍 TESTING CURRENT TIMEZONE AWARENESS")
    
    try:
        await database.connect()
        
        async with database.pool.acquire() as conn:
            # Test 1: Check database timezone
            db_timezone = await conn.fetchval("SHOW timezone;")
            print(f"✅ Database timezone: {db_timezone}")
            
            # Test 2: Check current time handling (FIXED)
            db_time = await conn.fetchval("SELECT NOW();")
            python_time = datetime.now(tz.utc)  # Use the renamed import
            
            print(f"✅ Database time (UTC): {db_time}")
            print(f"✅ Python time (UTC): {python_time}")
            print(f"✅ Time difference: {db_time - python_time}")
            
            # Test 3: Timezone-aware operations
            test_timestamp = await conn.fetchval("SELECT NOW()::timestamptz;")
            print(f"✅ Timestamp with timezone: {test_timestamp}")
            print(f"✅ Timestamp timezone: {test_timestamp.tzinfo}")
            
            # Test 4: Verify we can store and retrieve timestamps correctly
            await conn.execute("""
                CREATE TEMPORARY TABLE IF NOT EXISTS timezone_test (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    test_data TEXT
                );
            """)
            
            # Insert with current timestamp
            await conn.execute(
                "INSERT INTO timezone_test (test_data) VALUES ($1)",
                "timezone_aware_test"
            )
            
            # Retrieve and check the timestamp
            stored_time = await conn.fetchval(
                "SELECT created_at FROM timezone_test WHERE test_data = $1",
                "timezone_aware_test"
            )
            print(f"✅ Stored and retrieved timestamp: {stored_time}")
            print(f"✅ Stored timestamp timezone: {stored_time.tzinfo}")
            
        await database.close()
        print("✅ Timezone test completed successfully")
        
    except Exception as e:
        print(f"❌ Timezone test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_current_timezone())
