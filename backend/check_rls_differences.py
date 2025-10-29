import asyncio
import asyncpg
from app.core.config import settings

async def check_rls_differences():
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("🔍 COMPARING RLS POLICIES: POSTS vs JOURNALS")
        print("=" * 50)
        
        # 1. Check posts RLS policies
        print("1. POSTS RLS POLICIES:")
        posts_policies = await conn.fetch("""
            SELECT policyname, cmd, qual, with_check 
            FROM pg_policies 
            WHERE tablename = 'posts'
        """)
        for p in posts_policies:
            print(f"   {p['policyname']}: {p['cmd']}")
            if p['qual']: print(f"      Qual: {p['qual']}")
            if p['with_check']: print(f"      With Check: {p['with_check']}")
        print()
        
        # 2. Test posts insertion with context
        print("2. TESTING POSTS INSERTION WITH CONTEXT:")
        test_user_id = "d31ce60e-e013-44a9-97e3-dda4ee30d6d2"
        
        # Set context
        await conn.execute("SELECT set_current_user_id($1);", test_user_id)
        current_ctx = await conn.fetchval("SELECT current_setting('app.current_user_id', true);")
        print(f"   Context set to: {current_ctx}")
        
        # Try to insert a post
        try:
            result = await conn.execute("""
                INSERT INTO posts (user_id, content, visibility, is_anonymous)
                VALUES ($1, $2, $3, $4)
            """, test_user_id, "Test post via direct SQL", "public", False)
            print(f"   ✅ Posts insertion: {result}")
        except Exception as e:
            print(f"   ❌ Posts insertion failed: {e}")
        
        # 3. Test journals insertion with same context
        print("3. TESTING JOURNALS INSERTION WITH SAME CONTEXT:")
        try:
            result = await conn.execute("""
                INSERT INTO posts (user_id, content, content_type, visibility, is_anonymous)
                VALUES ($1, $2, $3, $4, $5)
            """, test_user_id, "Test journal via direct SQL", "journal", "private", False)
            print(f"   ✅ Journals insertion: {result}")
        except Exception as e:
            print(f"   ❌ Journals insertion failed: {e}")
        
        # 4. Check if there are multiple conflicting policies
        print("4. CHECKING FOR POLICY CONFLICTS:")
        policy_counts = await conn.fetchval("""
            SELECT COUNT(*) FROM pg_policies WHERE tablename = 'posts'
        """)
        print(f"   Total posts policies: {policy_counts}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error during check: {e}")

asyncio.run(check_rls_differences())
