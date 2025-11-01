#!/usr/bin/env python3
"""
Completely seed the crisis system with test data for the upgraded schema
"""
import asyncio
import asyncpg
import os
import json
from datetime import date, timedelta
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

async def seed_crisis_complete():
    """Seed all crisis tables with comprehensive test data"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")

        # Get the test user
        user_id = await conn.fetchval("SELECT id FROM users WHERE email = 'developer_test@example.com'")
        if not user_id:
            print("❌ Test user not found")
            await conn.close()
            return

        print(f"👤 Seeding data for user: {user_id}")

        # SET RLS CONTEXT - This is crucial
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user_id))
        print("🔧 RLS context set")

        # 1. SEED USER CRISIS PREFERENCES
        print("\n1. 📝 Seeding user crisis preferences...")
        try:
            await conn.execute('''
                INSERT INTO user_crisis_preferences (
                    user_id, preferred_language, country_code, 
                    emergency_contact_instructions, medical_information, consent_to_contact
                ) VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (user_id) DO UPDATE SET
                    preferred_language = EXCLUDED.preferred_language,
                    country_code = EXCLUDED.country_code,
                    emergency_contact_instructions = EXCLUDED.emergency_contact_instructions,
                    medical_information = EXCLUDED.medical_information,
                    consent_to_contact = EXCLUDED.consent_to_contact,
                    updated_at = NOW()
            ''', user_id, 'en', 'US', 
               'Contact my emergency contacts in order listed. Sarah is primary.',
               'Allergies: Penicillin. Medications: None. Mental health: Anxiety.',
               True)
            print("   ✅ User crisis preferences seeded")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

        # 2. SEED EMERGENCY CONTACTS
        print("\n2. 👥 Seeding emergency contacts...")
        emergency_contacts = [
            {
                'name': 'Sarah Wilson',
                'relationship': 'Best Friend', 
                'phone_number': '+1-555-0101',
                'email': 'sarah.wilson@email.com',
                'is_primary': True,
                'can_receive_alerts': True,
                'notes': 'Available 24/7 for emergencies'
            },
            {
                'name': 'Dr. Michael Chen',
                'relationship': 'Therapist',
                'phone_number': '+1-555-0102', 
                'email': 'dr.chen@clinic.com',
                'is_primary': False,
                'can_receive_alerts': True,
                'notes': 'Therapist - available during business hours'
            },
            {
                'name': 'Maria Garcia',
                'relationship': 'Sister',
                'phone_number': '+1-555-0103',
                'email': 'maria.garcia@email.com',
                'is_primary': False, 
                'can_receive_alerts': True,
                'notes': 'Family contact'
            }
        ]

        for contact in emergency_contacts:
            try:
                await conn.execute('''
                    INSERT INTO emergency_contacts (
                        user_id, name, relationship, phone_number, email, 
                        is_primary, can_receive_alerts, notes
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ''', user_id, contact['name'], contact['relationship'], 
                   contact['phone_number'], contact['email'],
                   contact['is_primary'], contact['can_receive_alerts'], 
                   contact['notes'])
                print(f"   ✅ {contact['name']} added")
            except Exception as e:
                print(f"   ❌ Failed to add {contact['name']}: {e}")

        # 3. SEED SAFETY PLANS (using ACTUAL schema)
        print("\n3. 🛡️ Seeding safety plans...")
        safety_plans = [
            {
                'plan_name': 'My Main Safety Plan',
                'personal_warning_signs': ['Feeling overwhelmed', 'Sleeping too much', 'Isolating myself'],
                'early_warning_triggers': ['Work stress', 'Conflict with family', 'Financial worries'],
                'internal_coping_strategies': ['Practice deep breathing', 'Listen to calming music', 'Write in journal'],
                'social_coping_strategies': ['Call Sarah', 'Text Maria', 'Visit family'],
                'professional_coping_strategies': ['Schedule therapy session', 'Call crisis line', 'Email Dr. Chen'],
                'emergency_contact_instructions': 'Contact Sarah first, then Maria. Dr. Chen for professional support.',
                'crisis_line_preferences': ['988 Suicide Prevention', 'Crisis Text Line'],
                'means_restriction_plan': 'Keep medications locked away. Remove alcohol from home.',
                'safe_locations': ['Local park', 'Coffee shop downtown', 'Sisters house'],
                'is_active': True
            },
            {
                'plan_name': 'Work Stress Safety Plan', 
                'personal_warning_signs': ['Irritability at work', 'Difficulty concentrating', 'Avoiding colleagues'],
                'internal_coping_strategies': ['Take short breaks', 'Practice mindfulness', 'Use stress ball'],
                'social_coping_strategies': ['Talk to manager', 'Lunch with coworker', 'Call friend after work'],
                'is_active': False
            }
        ]

        for plan in safety_plans:
            try:
                await conn.execute('''
                    INSERT INTO safety_plans (
                        user_id, plan_name, plan_version, is_active,
                        personal_warning_signs, early_warning_triggers,
                        internal_coping_strategies, social_coping_strategies, professional_coping_strategies,
                        emergency_contact_instructions, crisis_line_preferences,
                        means_restriction_plan, safe_locations,
                        last_reviewed_date, next_review_date
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ''', user_id,
                   plan['plan_name'],
                   plan.get('plan_version', 1),
                   plan.get('is_active', True),
                   plan.get('personal_warning_signs', []),
                   plan.get('early_warning_triggers', []),
                   plan.get('internal_coping_strategies', []),
                   plan.get('social_coping_strategies', []),
                   plan.get('professional_coping_strategies', []),
                   plan.get('emergency_contact_instructions'),
                   plan.get('crisis_line_preferences', []),
                   plan.get('means_restriction_plan'),
                   plan.get('safe_locations', []),
                   date.today(),
                   date.today() + timedelta(days=30)
                )
                print(f"   ✅ {plan['plan_name']} added")
            except Exception as e:
                print(f"   ❌ Failed to add {plan['plan_name']}: {e}")

        # 4. SEED WELLNESS CHECKINS
        print("\n4. 💪 Seeding wellness checkins...")
        checkin_dates = [date.today() - timedelta(days=i) for i in range(7)]
        
        for i, checkin_date in enumerate(checkin_dates):
            try:
                await conn.execute('''
                    INSERT INTO wellness_checkins (
                        user_id, checkin_date, mood_rating, anxiety_level,
                        sleep_quality, safety_concerns, coping_strategies_used,
                        support_needed, notes
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''', user_id, checkin_date,
                   max(1, min(10, 5 + i)),  # mood_rating between 1-10
                   max(1, min(10, 3 + i)),  # anxiety_level between 1-10  
                   max(1, min(5, 3)),       # sleep_quality between 1-5
                   i == 0,                  # safety_concerns on first day
                   ['Deep breathing', 'Walk outside'][:i%2+1],
                   i % 3 == 0,              # support_needed every 3 days
                   f'Checkin for {checkin_date}. Feeling {"better" if i < 3 else "okay"}.'
                )
                print(f"   ✅ Checkin for {checkin_date} added")
            except Exception as e:
                print(f"   ❌ Failed to add checkin for {checkin_date}: {e}")

        # 5. SEED CRISIS ALERTS
        print("\n5. 🚨 Seeding crisis alerts...")
        crisis_alerts = [
            {
                'alert_type': 'wellness_check',
                'severity_level': 'low', 
                'message': 'Routine wellness check completed',
                'location_data': {'city': 'Seattle', 'state': 'WA'},
                'is_resolved': True,
                'resolved_at': '2025-10-30 20:00:00+00'
            },
            {
                'alert_type': 'safety_concern', 
                'severity_level': 'medium',
                'message': 'Experiencing increased anxiety, requested support contact',
                'location_data': {'city': 'Seattle', 'state': 'WA'},
                'is_resolved': False
            }
        ]

        for alert in crisis_alerts:
            try:
                await conn.execute('''
                    INSERT INTO crisis_alerts (
                        user_id, alert_type, severity_level, message, location_data,
                        is_resolved, resolved_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ''', user_id,
                   alert['alert_type'],
                   alert['severity_level'], 
                   alert['message'],
                   alert['location_data'],
                   alert.get('is_resolved', False),
                   alert.get('resolved_at')
                )
                print(f"   ✅ {alert['alert_type']} alert added")
            except Exception as e:
                print(f"   ❌ Failed to add {alert['alert_type']} alert: {e}")

        print("\n🎉 CRISIS SYSTEM SEEDING COMPLETE!")
        
        # Verify counts
        print("\n📊 VERIFICATION:")
        tables = {
            'user_crisis_preferences': 'user_id',
            'emergency_contacts': 'user_id', 
            'safety_plans': 'user_id',
            'wellness_checkins': 'user_id',
            'crisis_alerts': 'user_id'
        }
        
        for table, id_col in tables.items():
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table} WHERE {id_col} = $1', user_id)
            print(f"   {table}: {count} rows")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 SEEDING CRISIS SYSTEM WITH COMPLETE TEST DATA")
    asyncio.run(seed_crisis_complete())
