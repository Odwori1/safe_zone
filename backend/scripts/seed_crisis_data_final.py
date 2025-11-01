#!/usr/bin/env python3
"""
Seed crisis support system with test data - FINAL VERSION
Matches the ACTUAL table structures we discovered
"""
import asyncio
import asyncpg
import os
import json
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

async def seed_crisis_data():
    """Seed crisis tables with test data matching ACTUAL table structure"""
    
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
        
        # Create sample emergency contacts (this worked already)
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
        
        # Create sample safety plans - USING ACTUAL COLUMN NAMES
        safety_plans = [
            {
                'user_id': user_id,
                'plan_name': 'My Main Safety Plan',
                'plan_version': 1,
                'is_active': True,
                'personal_warning_signs': ['Feeling overwhelmed', 'Sleeping too much or too little', 'Isolating myself'],
                'early_warning_triggers': ['Work stress', 'Conflict with family', 'Financial worries'],
                'internal_coping_strategies': ['Practice deep breathing', 'Listen to calming music', 'Write in journal'],
                'social_coping_strategies': ['Call Sarah', 'Text Maria', 'Visit family'],
                'professional_coping_strategies': ['Schedule therapy session', 'Call crisis line', 'Email Dr. Chen'],
                'emergency_contact_instructions': 'Contact Sarah first, then Maria. Dr. Chen for professional support.',
                'crisis_line_preferences': ['988 Suicide Prevention', 'Crisis Text Line'],
                'means_restriction_plan': 'Keep medications locked away. Remove alcohol from home.',
                'safe_locations': ['Local park', 'Coffee shop downtown', 'Sisters house'],
                'last_reviewed_date': date.today(),
                'next_review_date': date.today() + timedelta(days=30)
            },
            {
                'user_id': user_id,
                'plan_name': 'Work Stress Safety Plan',
                'plan_version': 1,
                'is_active': False,
                'personal_warning_signs': ['Feeling irritable at work', 'Difficulty concentrating', 'Avoiding coworkers'],
                'internal_coping_strategies': ['Take short breaks', 'Practice mindfulness', 'Use positive self-talk'],
                'social_coping_strategies': ['Talk to manager', 'Call support person', 'Lunch with coworker'],
                'professional_coping_strategies': ['Use EAP services', 'Schedule meeting with HR'],
                'safe_locations': ['Break room', 'Outside courtyard', 'Quiet conference room']
            }
        ]
        
        print("🛡️ Seeding safety plans...")
        for plan in safety_plans:
            await conn.execute("""
                INSERT INTO safety_plans (
                    user_id, plan_name, plan_version, is_active,
                    personal_warning_signs, early_warning_triggers,
                    internal_coping_strategies, social_coping_strategies, professional_coping_strategies,
                    emergency_contact_instructions, crisis_line_preferences,
                    means_restriction_plan, safe_locations,
                    last_reviewed_date, next_review_date
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT DO NOTHING
            """, 
                plan['user_id'], plan['plan_name'], plan.get('plan_version', 1),
                plan.get('is_active', True), plan.get('personal_warning_signs'),
                plan.get('early_warning_triggers'), plan.get('internal_coping_strategies'),
                plan.get('social_coping_strategies'), plan.get('professional_coping_strategies'),
                plan.get('emergency_contact_instructions'), plan.get('crisis_line_preferences'),
                plan.get('means_restriction_plan'), plan.get('safe_locations'),
                plan.get('last_reviewed_date'), plan.get('next_review_date')
            )
        print(f"✅ Created {len(safety_plans)} safety plans")
        
        # Create sample wellness checkins for the past week - USING ACTUAL COLUMN NAMES
        print("💚 Seeding wellness checkins...")
        for days_ago in range(7):
            checkin_date = date.today() - timedelta(days=days_ago)
            mood = max(1, min(10, 7 - days_ago + (1 if days_ago % 2 == 0 else -1)))  # Varying mood
            anxiety = max(1, min(10, 3 + days_ago % 3))
            sleep = max(1, min(5, 4 - days_ago % 2))
            
            await conn.execute("""
                INSERT INTO wellness_checkins (
                    user_id, checkin_date, mood_rating, anxiety_level, sleep_quality,
                    safety_concerns, safety_concerns_details, coping_strategies_used, 
                    support_needed, support_type, notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (user_id, checkin_date) DO UPDATE SET
                    mood_rating = EXCLUDED.mood_rating,
                    anxiety_level = EXCLUDED.anxiety_level,
                    sleep_quality = EXCLUDED.sleep_quality,
                    safety_concerns = EXCLUDED.safety_concerns,
                    safety_concerns_details = EXCLUDED.safety_concerns_details,
                    coping_strategies_used = EXCLUDED.coping_strategies_used,
                    support_needed = EXCLUDED.support_needed,
                    support_type = EXCLUDED.support_type,
                    notes = EXCLUDED.notes
            """, 
                user_id, checkin_date, mood, anxiety, sleep,
                days_ago == 2,  # One day with safety concerns
                "Feeling unsafe at home" if days_ago == 2 else None,
                ['Deep breathing', 'Walk outside'] if days_ago % 2 == 0 else ['Journaling', 'Music'],
                days_ago == 1,  # One day needing support
                'Therapy session' if days_ago == 1 else None,
                f"Feeling {'better' if mood > 6 else 'okay'} today. {'Need to practice more self-care.' if mood < 5 else ''}"
            )
        print("✅ Created 7 days of wellness checkins")
        
        # Create sample crisis alerts - USING ACTUAL COLUMN NAMES
        crisis_alerts = [
            {
                'user_id': user_id,
                'alert_type': 'wellness_check',
                'severity_level': 'low',
                'message': 'Routine wellness check completed',
                'location_data': json.dumps({'city': 'Seattle', 'state': 'WA'}),  # Convert to JSON string
                'is_resolved': True,
                'resolved_at': date.today() - timedelta(days=1),
                'resolution_notes': 'User confirmed they are safe'
            },
            {
                'user_id': user_id,
                'alert_type': 'safety_concern',
                'severity_level': 'medium', 
                'message': 'Reported safety concerns in wellness checkin',
                'location_data': json.dumps({'city': 'Seattle', 'state': 'WA'}),  # Convert to JSON string
                'is_resolved': True,
                'resolved_at': date.today() - timedelta(days=2),
                'resolution_notes': 'User contacted emergency contact and feels safer now'
            },
            {
                'user_id': user_id,
                'alert_type': 'sos',
                'severity_level': 'high',
                'message': 'User activated SOS feature - immediate assistance needed',
                'location_data': json.dumps({  # Convert to JSON string
                    'city': 'Seattle', 
                    'state': 'WA', 
                    'latitude': 47.6062, 
                    'longitude': -122.3321
                }),
                'is_resolved': False
            }
        ]
        
        print("🚨 Seeding crisis alerts...")
        for alert in crisis_alerts:
            await conn.execute("""
                INSERT INTO crisis_alerts (
                    user_id, alert_type, severity_level, message, location_data, 
                    is_resolved, resolved_at, resolution_notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT DO NOTHING
            """, 
                alert['user_id'], alert['alert_type'], alert['severity_level'],
                alert['message'], alert['location_data'], alert['is_resolved'],
                alert.get('resolved_at'), alert.get('resolution_notes')
            )
        print(f"✅ Created {len(crisis_alerts)} crisis alerts")
        
        # Create user crisis preferences - USING ACTUAL COLUMN NAMES
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
            'Allergies: Penicillin. Current medications: None. Mental health diagnosis: Anxiety.',
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
