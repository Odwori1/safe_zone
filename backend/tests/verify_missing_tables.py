"""
Verify the missing Phase 1 & 2 tables were created
"""

import asyncio
from app.database.database import database

async def verify_missing_tables():
    """Verify the missing tables are now created"""
    print("🔍 VERIFYING MISSING TABLES CREATION")
    print("=" * 50)
    
    missing_tables = [
        'password_reset_tokens',
        'reactions', 
        'saved_posts',
        'circles',
        'circle_members',
        'circle_posts'
    ]
    
    results = []
    
    try:
        await database.connect()
        async with database.pool.acquire() as conn:
            for table in missing_tables:
                exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = $1)",
                    table
                )
                if exists:
                    print(f"✅ {table} - CREATED")
                    results.append(True)
                    
                    # Check RLS is enabled
                    rls_enabled = await conn.fetchval(
                        "SELECT rowsecurity FROM pg_tables WHERE tablename = $1",
                        table
                    )
                    if rls_enabled:
                        print(f"   🔒 RLS: ENABLED")
                    else:
                        print(f"   ⚠️  RLS: DISABLED")
                        results.append(False)
                else:
                    print(f"❌ {table} - STILL MISSING")
                    results.append(False)
    
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    success = all(results)
    if success:
        print(f"\n🎉 ALL {len(missing_tables)} MISSING TABLES CREATED!")
    else:
        print(f"\n⚠️  Some tables still missing or RLS not enabled")
    
    return success

async def main():
    success = await verify_missing_tables()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
