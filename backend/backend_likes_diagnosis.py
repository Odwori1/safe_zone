import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def backend_diagnosis():
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        
        print("🔍 BACKEND LIKES DIAGNOSIS")
        print("=" * 50)
        
        # Test post ID that's failing
        POST_ID = "c8e1e8eb-43d7-4df0-9977-d43956aa1308"
        USER_ID = "8808956b-11fb-4253-91ef-98b9902ffbc8"
        
        print(f"Post ID: {POST_ID}")
        print(f"User ID: {USER_ID}")
        print("")
        
        # 1. Check if post exists and is accessible
        print("1. CHECKING POST:")
        print("-" * 20)
        
        await conn.execute("SELECT set_config('app.current_user_id', $1, false)", USER_ID)
        
        post = await conn.fetchrow("SELECT * FROM posts WHERE id = $1", POST_ID)
        if post:
            print(f"✅ Post exists:")
            print(f"   Content: {post['content'][:50]}...")
            print(f"   User ID: {post['user_id']}")
            print(f"   Visibility: {post['visibility']}")
            print(f"   Status: {post['status']}")
            print(f"   Moderation: {post['moderation_status']}")
        else:
            print("❌ Post not found or not accessible with RLS")
            return
        
        print("")
        
        # 2. Check if user can like this post (RLS test)
        print("2. RLS PERMISSION CHECK:")
        print("-" * 20)
        
        # Test if user can insert into post_likes
        try:
            test_like = await conn.fetchrow("""
                INSERT INTO post_likes (post_id, user_id) 
                VALUES ($1, $2) 
                RETURNING id
            """, POST_ID, USER_ID)
            
            if test_like:
                print("✅ User CAN like this post (RLS allows)")
                # Clean up test like
                await conn.execute("DELETE FROM post_likes WHERE id = $1", test_like['id'])
            else:
                print("❌ User CANNOT like this post (RLS blocks)")
                
        except Exception as e:
            print(f"❌ RLS Permission Error: {e}")
        
        print("")
        
        # 3. Check post_likes table structure and permissions
        print("3. POST_LIKES TABLE CHECK:")
        print("-" * 20)
        
        # Check table exists
        table_exists = await conn.fetchval("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'post_likes'
        """)
        print(f"Table exists: {'✅ YES' if table_exists else '❌ NO'}")
        
        # Check foreign key constraints
        fk_check = await conn.fetch("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'post_likes'
        """)
        
        if fk_check:
            print("✅ Foreign keys found:")
            for fk in fk_check:
                print(f"   {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        else:
            print("❌ No foreign keys found (this might be the issue!)")
        
        print("")
        
        # 4. Check RLS policies
        print("4. RLS POLICIES CHECK:")
        print("-" * 20)
        
        policies = await conn.fetch("""
            SELECT policyname, cmd, qual 
            FROM pg_policies 
            WHERE tablename = 'post_likes'
            ORDER BY policyname
        """)
        
        if policies:
            for policy in policies:
                print(f"✅ {policy['policyname']}: {policy['cmd']}")
                print(f"   Qual: {policy['qual'][:100]}...")
        else:
            print("❌ No RLS policies found")
        
        print("")
        
        # 5. Test the actual like operation that's failing
        print("5. TESTING LIKE OPERATION:")
        print("-" * 20)
        
        try:
            # This is what the backend CRUD does
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", USER_ID)
            
            result = await conn.execute("""
                INSERT INTO post_likes (post_id, user_id) 
                VALUES ($1, $2)
            """, POST_ID, USER_ID)
            
            if "INSERT 0 1" in result:
                print("✅ Like operation SUCCESSFUL")
                # Clean up
                await conn.execute("DELETE FROM post_likes WHERE post_id = $1 AND user_id = $2", POST_ID, USER_ID)
            else:
                print(f"❌ Like operation failed: {result}")
                
        except Exception as e:
            print(f"❌ Like operation error: {e}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")

asyncio.run(backend_diagnosis())
