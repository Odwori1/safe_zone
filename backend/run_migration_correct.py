import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    print("🗄️ RUNNING MIGRATION WITH CORRECT CONNECTION DETAILS")
    print("=" * 50)
    
    # Use the exact same connection details from .env
    db_config = {
        'host': os.getenv("DB_HOST", "127.0.0.1"),
        'port': int(os.getenv("DB_PORT", "5433")),
        'user': os.getenv("DB_USER", "safe_zone_user"),
        'password': os.getenv("DB_PASSWORD", "0791486006@safezone"),
        'database': os.getenv("DB_NAME", "safe_zone")
    }
    
    print(f"Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
        # Connect to database with correct details
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database successfully")
        
        # Read and execute our migration script
        with open('scripts/create_secure_file_metadata.sql', 'r') as f:
            migration_sql = f.read()
        
        print("📝 Executing migration...")
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
            
            # Show the created table structure
            columns = await conn.fetch(
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'file_metadata' ORDER BY ordinal_position"
            )
            print("📊 Table structure:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']}")
                
        else:
            print("❌ file_metadata table was not created")
        
        await conn.close()
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

asyncio.run(run_migration())
