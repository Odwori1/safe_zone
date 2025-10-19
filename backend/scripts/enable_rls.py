import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def enable_rls():
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'safe_zone_user'),
        'password': os.getenv('DB_PASSWORD', '0791486006@safezone'),
        'database': os.getenv('DB_NAME', 'safe_zone')
    }
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("🔐 Enabling Row Level Security...")
        
        # Enable RLS on all tables
        tables = ['users', 'posts', 'journals']
        
        for table in tables:
            # Enable RLS
            await conn.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;')
            print(f"✅ RLS enabled on {table}")
            
            # Drop existing policies if any
            await conn.execute(f'DROP POLICY IF EXISTS {table}_isolation_policy ON {table};')
            
            # Create isolation policies
            if table == 'users':
                # Users can only see/update their own data
                await conn.execute(f'''
                    CREATE POLICY {table}_isolation_policy ON {table}
                    FOR ALL USING (id = current_setting('app.current_user_id', true)::uuid);
                ''')
            else:
                # Posts and journals: users can only access their own data
                await conn.execute(f'''
                    CREATE POLICY {table}_isolation_policy ON {table}
                    FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
                ''')
            
            print(f"✅ Isolation policy created for {table}")
        
        # Create a function to set user context
        await conn.execute('''
            CREATE OR REPLACE FUNCTION set_current_user_id(user_id uuid)
            RETURNS void AS $$
            BEGIN
                PERFORM set_config('app.current_user_id', user_id::text, false);
            END;
            $$ LANGUAGE plpgsql;
        ''')
        print("✅ User context function created")
        
        # Verify RLS is enabled
        rls_status = await conn.fetch('''
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('users', 'posts', 'journals');
        ''')
        
        print("\n🔍 RLS Status Verification:")
        for row in rls_status:
            status = "✅ ENABLED" if row['rowsecurity'] else "❌ DISABLED"
            print(f"   {row['tablename']}: {status}")
        
        await conn.close()
        print("\n🎉 RLS configuration completed successfully!")
        
    except Exception as e:
        print(f"❌ RLS setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(enable_rls())
