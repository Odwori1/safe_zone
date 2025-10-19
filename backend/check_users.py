#!/usr/bin/env python3
"""
Check existing users in the database
"""

import asyncio
import asyncpg
from app.core.config import settings

async def check_users():
    conn = None
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        users = await conn.fetch("SELECT id, email, username, full_name FROM users LIMIT 10")
        print("📋 Existing users in database:")
        for user in users:
            print(f"  - ID: {user['id']}")
            print(f"    Email: {user['email']}")
            print(f"    Username: {user['username']}")
            print(f"    Full Name: {user['full_name']}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_users())
