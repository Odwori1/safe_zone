#!/usr/bin/env python3
"""
Create a fresh test user for crisis system testing
"""
import asyncio
from app.database.database import database
from uuid import uuid4
import asyncpg

async def create_fresh_test_user():
    """Create a fresh user for crisis testing"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("👤 CREATING FRESH TEST USER")
        
        # Create new user
        user_id = uuid4()
        email = f"crisis_test_{user_id.hex[:8]}@example.com"
        password_hash = "$2b$12$EXRkfkdmXn2gzds2SSitu.MJ9pi2a7W2Zp2d7TyBPDsB6xZgScCQ6"  # "TestPass123!"
        
        try:
            # Insert user
            await conn.execute('''
                INSERT INTO users (id, email, password_hash, username, full_name, timezone, is_active, is_verified)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', user_id, email, password_hash, "crisistester", "Crisis Test User", "UTC", True, True)
            
            print(f"✅ Created user: {email}")
            print(f"   User ID: {user_id}")
            print("   Password: TestPass123!")
            
            return user_id, email
            
        except Exception as e:
            print(f"❌ Failed to create user: {e}")
            return None, None

if __name__ == "__main__":
    user_id, email = asyncio.run(create_fresh_test_user())
    if user_id:
        print(f"\n🎉 Use these credentials for testing:")
        print(f"Email: {email}")
        print(f"Password: TestPass123!")
