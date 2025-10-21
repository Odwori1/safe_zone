# The error shows that Pydantic is trying to validate a full database record
# against FileUploadResponse schema, but the record has many more fields

# Let's create a simple test to see what the CRUD returns
import asyncio
from app.crud.file_metadata import file_metadata_crud
from app.core.config import settings
import asyncpg

async def test_crud_return():
    print("🔍 DEBUGGING CRUD RETURN VALUE")
    
    # Connect to database
    conn = await asyncpg.connect(settings.database_url)
    
    # Simulate what the CRUD does
    test_data = {
        "s3_key": "users/test/posts/test/videos/test.mp4",
        "file_type": "video", 
        "original_filename": "test.mp4",
        "file_size": 10485760,
        "mime_type": "video/mp4",
        "duration": 60
    }
    
    result = await conn.fetchrow(
        """
        INSERT INTO file_metadata 
        (user_id, post_id, s3_key, file_type, original_filename, 
         file_size, mime_type, duration, upload_status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
        """,
        'd31ce60e-e013-44a9-97e3-dda4ee30d6d2',  # test user ID
        None,  # no post_id
        test_data["s3_key"], test_data["file_type"],
        test_data["original_filename"], test_data["file_size"],
        test_data["mime_type"], test_data["duration"], "pending"
    )
    
    print("📊 Database returns:")
    print(f"Type: {type(result)}")
    print(f"Keys: {list(result.keys())}")
    print(f"Full record: {dict(result)}")
    
    await conn.close()

asyncio.run(test_crud_return())
