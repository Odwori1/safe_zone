import asyncio
import asyncpg
from uuid import UUID
from app.database.database import database
from app.schemas.post import PostCreate

async def debug_posts_crud():
    """Debug the posts CRUD create method"""
    print("🔍 DEBUGGING POSTS CRUD CREATE")
    print("=" * 50)
    
    try:
        # Initialize database connection
        await database.connect()
        
        # Test user ID (from your test user)
        test_user_id = UUID("d31ce60e-e013-44a9-97e3-dda4ee30d6d2")
        
        # Test post data
        post_data = PostCreate(
            content="Debug test post",
            visibility="public",
            is_anonymous=False
        )
        
        print(f"Test user_id: {test_user_id}")
        print(f"Test post data: {post_data.model_dump()}")
        
        # Test direct connection with context
        print("\n1. Testing direct connection with context:")
        async with database.pool.acquire() as conn:
            # Set context
            await conn.execute("SELECT set_current_user_id($1);", str(test_user_id))
            current_ctx = await conn.fetchval("SELECT current_setting('app.current_user_id', true);")
            print(f"   Context set to: {current_ctx}")
            
            # Try insert
            try:
                result = await conn.fetchrow("""
                    INSERT INTO posts (user_id, content, visibility, is_anonymous)
                    VALUES ($1, $2, $3, $4)
                    RETURNING *
                """, test_user_id, post_data.content, post_data.visibility, post_data.is_anonymous)
                print(f"   ✅ Direct insert successful: {result['id']}")
            except Exception as e:
                print(f"   ❌ Direct insert failed: {e}")
        
        # Test the actual CRUD method
        print("\n2. Testing CRUD method:")
        from app.crud.post import post_crud
        try:
            result = await post_crud.create(test_user_id, post_data)
            print(f"   ✅ CRUD create successful: {result['id']}")
        except Exception as e:
            print(f"   ❌ CRUD create failed: {e}")
            
        await database.close()
            
    except Exception as e:
        print(f"Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_posts_crud())
