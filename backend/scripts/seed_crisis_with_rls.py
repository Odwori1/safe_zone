#!/usr/bin/env python3
"""
Seed crisis data that works WITH RLS, not against it
"""
import asyncio
from app.database.database import database
from uuid import UUID

async def seed_with_rls():
    """Seed data that respects RLS policies"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🔐 SEEDING CRISIS DATA WITH RLS COMPLIANCE")
        print("==========================================")
        
        # Get test user
        user_id = await conn.fetchval("SELECT id FROM users WHERE email = 'developer_test@example.com'")
        if not user_id:
            print("❌ Test user not found")
            return
        
        print(f"👤 User ID: {user_id}")
        
        # The key: Set the user context for RLS
        print("🔧 Setting RLS user context...")
        await conn.execute("SET app.current_user_id TO $1", str(user_id))
        
        # 1. Create user crisis preferences
        print("\n1. 📝 Creating crisis preferences...")
        try:
            result = await conn.fetchrow('''
                INSERT INTO user_crisis_preferences (
                    user_id, preferred_language, country_code, consent_to_contact
                ) VALUES ($1, $2, $3, $4)
                RETURNING *
            ''', user_id, 'en', 'US', True)
            print(f"   ✅ Created: User ID {result['user_id']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # 2. Create emergency contacts
        print("\n2. 👥 Creating emergency contacts...")
        contacts = [
            ('Sarah Wilson', 'Sister', '+1-555-0101', True),
            ('Dr. Michael Chen', 'Therapist', '+1-555-0102', False),
            ('Maria Garcia', 'Friend', '+1-555-0103', False)
        ]
        
        for name, relationship, phone, is_primary in contacts:
            try:
                result = await conn.fetchrow('''
                    INSERT INTO emergency_contacts (
                        user_id, name, relationship, phone_number, is_primary
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                ''', user_id, name, relationship, phone, is_primary)
                print(f"   ✅ Created: {name}")
            except Exception as e:
                print(f"   ❌ Failed {name}: {e}")
        
        # 3. Create safety plan (using ACTUAL schema columns)
        print("\n3. 🛡️ Creating safety plan...")
        try:
            result = await conn.fetchrow('''
                INSERT INTO safety_plans (
                    user_id, plan_name, 
                    personal_warning_signs,  -- ACTUAL column name
                    internal_coping_strategies,  -- ACTUAL column name
                    social_coping_strategies  -- ACTUAL column name
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            ''', user_id, 'My Safety Plan', 
               ['Feeling overwhelmed', 'Isolating myself'],
               ['Deep breathing', 'Journaling'],
               ['Call a friend', 'Go for walk'])
            print(f"   ✅ Created safety plan: {result['id']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # 4. Create wellness checkin
        print("\n4. 💪 Creating wellness checkin...")
        try:
            result = await conn.fetchrow('''
                INSERT INTO wellness_checkins (
                    user_id, checkin_date, mood_rating, anxiety_level
                ) VALUES ($1, $2, $3, $4)
                RETURNING id
            ''', user_id, '2025-11-01', 6, 4)
            print(f"   ✅ Created checkin: {result['id']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # 5. Create crisis alert (with proper JSON string)
        print("\n5. 🚨 Creating crisis alert...")
        try:
            result = await conn.fetchrow('''
                INSERT INTO crisis_alerts (
                    user_id, alert_type, severity_level, message, location_data
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            ''', user_id, 'safety_concern', 'medium', 
               'Testing crisis system', '{"city": "Seattle", "country": "US"}')
            print(f"   ✅ Created alert: {result['id']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print("\n🎉 RLS-COMPLIANT SEEDING COMPLETE!")
        
        # Verify counts
        print("\n📊 VERIFICATION:")
        tables = ['user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
        for table in tables:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table} WHERE user_id = $1', user_id)
            print(f"   {table}: {count} rows")

if __name__ == "__main__":
    asyncio.run(seed_with_rls())
