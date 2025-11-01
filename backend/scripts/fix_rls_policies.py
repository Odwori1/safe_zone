#!/usr/bin/env python3
"""
Fix RLS policies for safety_plans and wellness_checkins
"""

import asyncio
import asyncpg

async def fix_rls_policies():
    print("🔧 Fixing RLS Policies...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # Fix safety_plans RLS policies
    print("Fixing safety_plans RLS policies...")
    try:
        # Drop existing policies
        await connection.execute("DROP POLICY IF EXISTS safety_plans_insert_policy ON safety_plans;")
        await connection.execute("DROP POLICY IF EXISTS safety_plans_select_policy ON safety_plans;")
        await connection.execute("DROP POLICY IF EXISTS safety_plans_update_policy ON safety_plans;")
        
        # Create proper policies with WITH CHECK
        await connection.execute('''
            CREATE POLICY user_safety_plans_policy ON safety_plans
            FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid)
            WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);
        ''')
        print("✅ Fixed safety_plans RLS policies")
    except Exception as e:
        print(f"❌ Failed to fix safety_plans policies: {e}")
    
    # Fix wellness_checkins RLS policies  
    print("Fixing wellness_checkins RLS policies...")
    try:
        # Drop existing policies
        await connection.execute("DROP POLICY IF EXISTS wellness_check_ins_insert_policy ON wellness_checkins;")
        await connection.execute("DROP POLICY IF EXISTS wellness_check_ins_select_policy ON wellness_checkins;")
        await connection.execute("DROP POLICY IF EXISTS wellness_check_ins_update_policy ON wellness_checkins;")
        
        # Create proper policies
        await connection.execute('''
            CREATE POLICY user_wellness_checkins_policy ON wellness_checkins
            FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid)
            WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);
        ''')
        print("✅ Fixed wellness_checkins RLS policies")
    except Exception as e:
        print(f"❌ Failed to fix wellness_checkins policies: {e}")
    
    await connection.close()
    print("🎉 RLS Policies Fixed!")

if __name__ == "__main__":
    asyncio.run(fix_rls_policies())
