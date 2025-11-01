#!/usr/bin/env python3
"""
Seed crisis support system with test data - CORRECT VERSION
Matches the actual table structure and handles RLS properly
"""
import asyncio
import asyncpg
import os
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

async def seed_crisis_data():
    """Seed crisis tables with test data matching actual table structure"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Get a user to create sample data for
        user_id = await conn.fetchval("SELECT id FROM users LIMIT 1")
        if not user_id:
            print("❌ No users found in database")
            await conn.close()
            return
        
        print(f"👤 Creating sample data for user: {user_id}")
        
        # SET RLS CONTEXT - This is crucial for RLS policies
        await conn.execute("SELECT set_current_user_id($1);", user_id)
        print("🔧 RLS context set for user")
        
        # Create sample emergency contacts
        emergency_contacts = [
            {
                'user_id': user_id,
                'name': 'Sarah Wilson',
                'relationship': 'Best Friend', 
                'phone_number': '+1-555-0101',
                'email': 'sarah.wilson@email.com',
                'is_primary': True,
                'can_receive_alerts': True,
                'notes': 'Available 24/7 for emergencies'
            },
            {
                'user_id': user_id,
                'name': 'Dr. Michael Chen',
                'relationship': 'Therapist',
                'phone_number': '+1-555-0102',
                'email': 'dr.chen@clinic.com',
                'is_primary': False,
                'can_receive_alerts': True,
                'notes': 'Office hours: Mon-Fri 9am-5pm'
            },
            {
                'user_id': user_id,
                'name': 'Maria Garcia',
                'relationship': 'Sister',
                'phone_number': '+1-555-0103',
                'email': 'maria.g@email.com',
                'is_primary': False,
                'can_receive_alerts': True,
                'notes': 'Very supportive and understanding'
            }
        ]
        
        print("📞 Seeding emergency contacts...")
        for contact in emergency_contacts:
            await conn.execute("""
                INSERT INTO emergency_contacts (
                    user_id, name, relationship, phone_number, email, 
                    is_primary, can_receive_alerts, notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT DO NOTHING
            """, 
                contact['user_id'], contact['name'], contact['relationship'],
                contact['phone_number'], contact['email'], contact['is_primary'],
                contact['can_receive_alerts'], contact['notes']
            )
        print(f"✅ Created {len(emergency_contacts)} emergency contacts")
        
        # Create sample safety plans
        safety_plans = [
            {
                'user_id': user_id,
                'plan_name': 'My Main Safety Plan',
                'warning_signs': ['Feeling overwhelmed', 'Sleeping too much or too little', 'Isolating myself'],
                'internal_coping_strategies': ['Practice deep breathing', 'Listen to calming music', 'Write in journal'],
                'external_coping_strategies': ['Go for a walk outside', 'Call a friend', 'Watch a favorite movie'],
                'social_contacts': {'friends': ['Sarah', 'Maria'], 'family': ['Mom', 'Sister']},
                'professional_contacts': {'therapist': 'Dr. Chen', 'crisis_line': '988'},
                'environment_safety': ['Remove alcohol from home', 'Keep medications locked', 'Create calming space'],
                'reasons_for_living': ['My family loves me', 'I want to see my dreams come true', 'My pets need me'],
                'is_active': True
            },
            {
                'user_id': user_id,
                'plan_name': 'Work Stress Safety Plan',
                'warning_signs': ['Feeling irritable at work', 'Difficulty concentrating', 'Avoiding coworkers'],
                'internal_coping_strategies': ['Take short breaks', 'Practice mindfulness', 'Use positive self-talk'],
                'external_coping_strategies': ['Talk to manager', 'Step outside for fresh air', 'Call support person'],
                'reasons_for_living': ['I enjoy my work most days', 'Colleagues who support me', 'Career goals'],
                'is_active': False
            }
        ]
        
        print("🛡️ Seeding safety plans...")
        for plan in safety_plans:
            await conn.execute("""
                INSERT INTO safety_plans (
                    user_id, plan_name, warning_signs, internal_coping_strategies,
                    external_coping_strategies, social_contacts, professional_contacts,
                    environment_safety, reasons_for_living, is_active
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT DO NOTHING
            """, 
                plan['user_id'], plan['plan_name'], plan['warning_signs'],
                plan['internal_coping_strategies'], plan['external_coping_strategies'],
                plan.get('social_contacts'), plan.get('professional_contacts'),
                plan.get('environment_safety'), plan['reasons_for_living'], plan['is_active']
            )
        print(f"✅ Created {len(safety_plans)} safety plans")
        
        # Create sample wellness checkins for the past week
        print("💚 Seeding wellness checkins...")
        for days_ago in range(7):
            checkin_date = date.today() - timedelta(days=days_ago)
            mood = max(1, min(10, 7 - days_ago + (1 if days_ago % 2 == 0 else -1)))  # Varying mood
            anxiety = max(1, min(10, 3 + days_ago % 3))
            sleep = max(1, min(5, 4 - days_ago % 2))
            
            await conn.execute("""
                INSERT INTO wellness_checkins (
                    user_id, checkin_date, mood_rating, anxiety_level, sleep_quality,
                    safety_concerns, coping_strategies_used, support_needed, notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (user_id, checkin_date) DO UPDATE SET
                    mood_rating = EXCLUDED.mood_rating,
                    anxiety_level = EXCLUDED.anxiety_level,
                    sleep_quality = EXCLUDED.sleep_quality,
                    safety_concerns = EXCLUDED.safety_concerns,
                    coping_strategies_used = EXCLUDED.coping_strategies_used,
                    support_needed = EXCLUDED.support_needed,
                    notes = EXCLUDED.notes
            """, 
                user_id, checkin_date, mood, anxiety, sleep,
                days_ago == 2,  # One day with safety concerns
                ['Deep breathing', 'Walk outside'] if days_ago % 2 == 0 else ['Journaling', 'Music'],
                days_ago == 1,  # One day needing support
                f"Feeling {'better' if mood > 6 else 'okay'} today. {'Need to practice more self-care.' if mood < 5 else ''}"
            )
        print("✅ Created 7 days of wellness checkins")
        
        # Create sample crisis alerts
        crisis_alerts = [
            {
                'user_id': user_id,
                'alert_type': 'wellness_check',
                'severity_level': 'low',
                'message': 'Routine wellness check completed',
                'location_data': {'city': 'Seattle', 'state': 'WA'},
                'is_resolved': True
            },
            {
                'user_id': user_id,
                'alert_type': 'safety_concern',
                'severity_level': 'medium', 
                'message': 'Reported safety concerns in wellness checkin',
                'location_data': {'city': 'Seattle', 'state': 'WA'},
                'is_resolved': True
            },
            {
                'user_id': user_id,
                'alert_type': 'sos',
                'severity_level': 'high',
                'message': 'User activated SOS feature',
                'location_data': {'city': 'Seattle', 'state': 'WA'},
                'is_resolved': False
            }
        ]
        
        print("🚨 Seeding crisis alerts...")
        for alert in crisis_alerts:
            await conn.execute("""
                INSERT INTO crisis_alerts (
                    user_id, alert_type, severity_level, message, location_data, is_resolved
                ) VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT DO NOTHING
            """, 
                alert['user_id'], alert['alert_type'], alert['severity_level'],
                alert['message'], alert['location_data'], alert['is_resolved']
            )
        print(f"✅ Created {len(crisis_alerts)} crisis alerts")
        
        # Create user crisis preferences
        print("⚙️ Seeding user crisis preferences...")
        await conn.execute("""
            INSERT INTO user_crisis_preferences (
                user_id, preferred_language, country_code, 
                emergency_contact_instructions, medical_information, consent_to_contact
            ) VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE SET
                preferred_language = EXCLUDED.preferred_language,
                country_code = EXCLUDED.country_code,
                emergency_contact_instructions = EXCLUDED.emergency_contact_instructions,
                medical_information = EXCLUDED.medical_information,
                consent_to_contact = EXCLUDED.consent_to_contact
        """, 
            user_id, 'en', 'US',
            'Please contact my emergency contacts in the order listed. Sarah is my primary contact.',
            'Allergies: Penicillin. Current medications: None.',
            True
        )
        print("✅ Created user crisis preferences")
        
        # Verify what was created
        print("\n🔍 Final Verification:")
        
        contact_count = await conn.fetchval("SELECT COUNT(*) FROM emergency_contacts WHERE user_id = $1", user_id)
        print(f"   Emergency contacts: {contact_count}")
        
        safety_plan_count = await conn.fetchval("SELECT COUNT(*) FROM safety_plans WHERE user_id = $1", user_id)
        print(f"   Safety plans: {safety_plan_count}")
        
        wellness_count = await conn.fetchval("SELECT COUNT(*) FROM wellness_checkins WHERE user_id = $1", user_id)
        print(f"   Wellness checkins: {wellness_count}")
        
        alert_count = await conn.fetchval("SELECT COUNT(*) FROM crisis_alerts WHERE user_id = $1", user_id)
        print(f"   Crisis alerts: {alert_count}")
        
        resource_count = await conn.fetchval("SELECT COUNT(*) FROM crisis_resources")
        print(f"   Crisis resources: {resource_count} (already existed)")
        
        preferences_count = await conn.fetchval("SELECT COUNT(*) FROM user_crisis_preferences WHERE user_id = $1", user_id)
        print(f"   User preferences: {preferences_count}")
        
        await conn.close()
        print("\n🎉 Crisis support system data seeding completed!")
        print("\n📋 Available endpoints to test:")
        print("   GET  /api/v1/crisis-support/resources/")
        print("   GET  /api/v1/crisis-support/emergency-contacts/")
        print("   GET  /api/v1/crisis-support/safety-plans/")
        print("   GET  /api/v1/crisis-support/wellness-checkins/")
        print("   GET  /api/v1/crisis-support/crisis-alerts/")
        print("   GET  /api/v1/crisis-support/preferences/")
        
    except Exception as e:
        print(f"❌ Error seeding crisis data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_crisis_data())
