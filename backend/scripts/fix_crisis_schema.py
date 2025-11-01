#!/usr/bin/env python3
"""
Fix crisis support system schema issues
"""
import asyncio
import asyncpg
from uuid import UUID
from app.database.database import database

async def fix_crisis_schema():
    """Fix all identified schema issues"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🔧 FIXING CRISIS SYSTEM SCHEMA...")
        
        # 1. Fix safety_plans table - add missing columns
        print("1. Updating safety_plans table...")
        try:
            await conn.execute('''
                ALTER TABLE safety_plans 
                ADD COLUMN IF NOT EXISTS warning_signs TEXT[],
                ADD COLUMN IF NOT EXISTS internal_coping_strategies TEXT[],
                ADD COLUMN IF NOT EXISTS external_coping_strategies TEXT[],
                ADD COLUMN IF NOT EXISTS social_contacts JSONB,
                ADD COLUMN IF NOT EXISTS professional_contacts JSONB,
                ADD COLUMN IF NOT EXISTS environment_safety TEXT[],
                ADD COLUMN IF NOT EXISTS reasons_for_living TEXT[];
            ''')
            print("   ✅ Added missing columns to safety_plans")
        except Exception as e:
            print(f"   ⚠️  Could not add columns: {e}")
        
        # 2. Fix crisis_alerts location_data type
        print("2. Updating crisis_alerts table...")
        try:
            await conn.execute('''
                ALTER TABLE crisis_alerts 
                ALTER COLUMN location_data TYPE JSONB USING location_data::jsonb;
            ''')
            print("   ✅ Fixed location_data type to JSONB")
        except Exception as e:
            print(f"   ⚠️  Could not update location_data: {e}")
        
        # 3. Ensure RLS policies are correct
        print("3. Checking RLS policies...")
        
        # Drop and recreate RLS policies with proper user matching
        tables = ['user_crisis_preferences', 'emergency_contacts', 'wellness_checkins', 'safety_plans', 'crisis_alerts']
        
        for table in tables:
            try:
                # Drop existing policies
                await conn.execute(f'DROP POLICY IF EXISTS "Users can manage their own {table}" ON {table}')
                await conn.execute(f'DROP POLICY IF EXISTS "Users can insert their own {table}" ON {table}')
                await conn.execute(f'DROP POLICY IF EXISTS "Users can view their own {table}" ON {table}')
                await conn.execute(f'DROP POLICY IF EXISTS "Users can update their own {table}" ON {table}')
                await conn.execute(f'DROP POLICY IF EXISTS "Users can delete their own {table}" ON {table}')
                
                # Create new policies
                await conn.execute(f'''
                    CREATE POLICY "Users can manage their own {table}" ON {table}
                    FOR ALL USING (user_id = auth.uid())
                    WITH CHECK (user_id = auth.uid());
                ''')
                print(f"   ✅ Recreated RLS policy for {table}")
            except Exception as e:
                print(f"   ⚠️  Could not update RLS for {table}: {e}")
        
        print("🎉 SCHEMA FIXES COMPLETED!")

if __name__ == "__main__":
    asyncio.run(fix_crisis_schema())
