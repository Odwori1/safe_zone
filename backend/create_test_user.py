#!/usr/bin/env python3
"""
Create a test user for API testing
"""

import asyncio
import asyncpg
from app.core.config import settings
from app.core.security import get_password_hash

async def create_test_user():
    conn = None
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        test_email = "api_test@example.com"
        test_username = "apitestuser"
        test_password = "testpassword123"
        test_full_name = "API Test User"
        
        # Check if user already exists
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", test_email
        )
        
        if existing_user:
            print(f"✅ Test user already exists: {test_email}")
            # Update password to known value
            hashed_password = get_password_hash(test_password)
            await conn.execute(
                "UPDATE users SET hashed_password = $1 WHERE email = $2",
                hashed_password, test_email
            )
            print("✅ Test user password updated")
        else:
            # Create new test user
            hashed_password = get_password_hash(test_password)
            await conn.execute("""
                INSERT INTO users (email, username, full_name, hashed_password, is_active)
                VALUES ($1, $2, $3, $4, true)
            """, test_email, test_username, test_full_name, hashed_password)
            print(f"✅ Test user created: {test_email}")
        
        print(f"📋 Test credentials:")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Username: {test_username}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())
