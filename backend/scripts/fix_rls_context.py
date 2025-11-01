#!/usr/bin/env python3
"""
Fix RLS context issue by checking current user setting
"""
import asyncio
from app.database.database import database
from uuid import UUID

async def check_rls_issue():
    """Check why RLS is blocking inserts"""
    await database.connect()
    
    user_id = UUID('a1a6ae52-69bb-4bba-82e1-da79c8340517')
    
    async with database.pool.acquire() as conn:
        print("🔍 CHECKING RLS CONTEXT ISSUE")
        print("=============================")
        
        # Check if we can set the user context
        try:
            await conn.execute("SET app.current_user_id TO 'a1a6ae52-69bb-4bba-82e1-da79c8340517'")
            print("✅ Set user context")
            
            # Now try to insert
            result = await conn.fetchrow('''
                INSERT INTO user_crisis_preferences 
                (user_id, preferred_language, country_code, consent_to_contact)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            ''', user_id, 'en', 'US', True)
            print("✅ Successfully inserted with context:", result['id'])
            
        except Exception as e:
            print(f"❌ Still failed: {e}")
            
        # Reset context
        await conn.execute("RESET app.current_user_id")

if __name__ == "__main__":
    asyncio.run(check_rls_issue())
