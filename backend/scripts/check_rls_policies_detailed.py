#!/usr/bin/env python3
"""
Check RLS policies in detail to understand what's expected
"""
import asyncio
from app.database.database import database

async def check_rls_policies():
    """Check what RLS policies exist and what they expect"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🔐 CHECKING RLS POLICIES DETAILS")
        print("================================")
        
        crisis_tables = [
            'user_crisis_preferences',
            'emergency_contacts', 
            'safety_plans',
            'wellness_checkins',
            'crisis_alerts'
        ]
        
        for table in crisis_tables:
            print(f"\n📋 TABLE: {table}")
            print("-" * 40)
            
            # Check RLS status
            rls_enabled = await conn.fetchval("""
                SELECT rowsecurity
                FROM pg_tables
                WHERE tablename = $1 AND schemaname = 'public'
            """, table)
            print(f"RLS Enabled: {rls_enabled}")
            
            # Check policies
            policies = await conn.fetch("""
                SELECT policyname, permissive, roles, cmd, qual
                FROM pg_policies
                WHERE tablename = $1 AND schemaname = 'public'
                ORDER BY cmd, policyname
            """, table)
            
            for policy in policies:
                print(f"  Policy: {policy['policyname']}")
                print(f"    Command: {policy['cmd']}")
                print(f"    Condition: {policy['qual']}")
                print(f"    Roles: {policy['roles']}")
                print("")
            
            # Check if we can set the user context
            try:
                user_id = await conn.fetchval("SELECT id FROM users WHERE email = 'developer_test@example.com'")
                if user_id:
                    await conn.execute("SET app.current_user_id TO $1", str(user_id))
                    print(f"  ✅ Can set app.current_user_id to: {user_id}")
                    
                    # Test if we can insert with context set
                    if table == 'user_crisis_preferences':
                        test_insert = await conn.fetchval(f"""
                            INSERT INTO {table} (user_id, preferred_language, consent_to_contact)
                            VALUES ($1, 'en', true)
                            RETURNING user_id
                        """, user_id)
                        if test_insert:
                            print(f"  ✅ INSERT works with RLS context set")
                            # Clean up
                            await conn.execute(f"DELETE FROM {table} WHERE user_id = $1", user_id)
                else:
                    print("  ❌ Test user not found")
            except Exception as e:
                print(f"  ❌ Cannot set context or insert: {e}")

if __name__ == "__main__":
    asyncio.run(check_rls_policies())
