"""
Quick test to verify Phase 6 database setup
"""

import asyncio
from app.database.database import database

async def test_database_connection():
    """Test database connection and table creation"""
    try:
        # Initialize database connection
        await database.connect()
        print("✅ Database connection established")
        
        async with database.pool.acquire() as conn:
            # Check Phase 6 tables
            tables = [
                'telehealth_sessions',
                'emr_connections', 
                'community_milestones',
                'success_stories',
                'user_sessions',
                'device_sync',
                'tutorial_progress'
            ]
            
            for table in tables:
                result = await conn.fetchrow(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = $1)",
                    table
                )
                if result and result['exists']:
                    print(f"✅ Table {table} exists")
                else:
                    print(f"❌ Table {table} does not exist")
            
            # Check RLS status
            for table in tables:
                result = await conn.fetchrow(
                    "SELECT rowsecurity FROM pg_tables WHERE tablename = $1",
                    table
                )
                if result:
                    status = "ENABLED" if result['rowsecurity'] else "DISABLED"
                    print(f"✅ RLS for {table}: {status}")
                else:
                    print(f"❌ Could not check RLS for {table}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def main():
    print("🔧 Testing Phase 6 Database Setup")
    print("=" * 40)
    success = await test_database_connection()
    if success:
        print("🎉 Phase 6 database setup completed successfully!")
    else:
        print("🚨 Phase 6 database setup has issues!")

if __name__ == "__main__":
    asyncio.run(main())
