import asyncio
import asyncpg
from app.core.config import settings

async def check_posts_structure():
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("🔍 CHECKING POSTS TABLE STRUCTURE")
        print("=" * 50)
        
        # Check columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'posts'
            ORDER BY ordinal_position;
        """)
        print("POSTS TABLE COLUMNS:")
        for col in columns:
            print(f"   {col['column_name']} ({col['data_type']}) - nullable: {col['is_nullable']}")
        print()
        
        # Check constraints
        constraints = await conn.fetch("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'posts';
        """)
        print("POSTS TABLE CONSTRAINTS:")
        for con in constraints:
            print(f"   {con['constraint_name']} ({con['constraint_type']})")
        print()
        
        # Check sample data
        sample = await conn.fetch("SELECT * FROM posts LIMIT 1;")
        if sample:
            print("SAMPLE POST DATA:")
            for key, value in dict(sample[0]).items():
                print(f"   {key}: {value}")
        else:
            print("No posts in database")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_posts_structure())
