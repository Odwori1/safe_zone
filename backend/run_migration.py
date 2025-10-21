import asyncpg
import asyncio
import os
from app.core.config import settings

async def run_migration():
    print("🗄️ RUNNING SECURE FILE METADATA MIGRATION")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(settings.database_url)
        print("✅ Connected to database")
        
        # Read and execute migration script
        with open('scripts/create_secure_file_metadata.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute the migration
        await conn.execute(migration_sql)
        print("✅ Migration executed successfully")
        
        # Verify the table was created
        table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'file_metadata')"
        )
        
        if table_exists:
            print("✅ file_metadata table created successfully")
            
            # Check RLS is enabled
            rls_enabled = await conn.fetchval(
                "SELECT relrowsecurity FROM pg_class WHERE relname = 'file_metadata'"
            )
            print(f"✅ RLS enabled: {rls_enabled}")
            
        else:
            print("❌ file_metadata table was not created")
        
        await conn.close()
        print("✅ Migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

asyncio.run(run_migration())
