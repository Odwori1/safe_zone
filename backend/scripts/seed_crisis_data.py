#!/usr/bin/env python3
"""
Seed crisis support system with test data
"""
import asyncio
import asyncpg
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

async def seed_crisis_data():
    """Seed crisis tables with test data"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Seed crisis resources
        crisis_resources = [
            {
                'name': 'National Suicide Prevention Lifeline',
                'category': 'suicide_prevention',
                'description': '24/7 free and confidential support for people in distress',
                'phone_number': '988',
                'website_url': 'https://suicidepreventionlifeline.org',
                'is_24_7': True,
                'languages_supported': 'English, Spanish',
                'is_verified': True
            },
            {
                'name': 'Crisis Text Line',
                'category': 'crisis_support',
                'description': 'Free 24/7 text support for any crisis',
                'phone_number': None,
                'text_line': 'Text HOME to 741741',
                'website_url': 'https://www.crisistextline.org',
                'is_24_7': True,
                'languages_supported': 'English',
                'is_verified': True
            },
            {
                'name': 'SAMHSA National Helpline',
                'category': 'substance_abuse',
                'description': 'Treatment referral and information service',
                'phone_number': '1-800-662-4357',
                'website_url': 'https://www.samhsa.gov',
                'is_24_7': True,
                'languages_supported': 'English, Spanish',
                'is_verified': True
            },
            {
                'name': 'National Domestic Violence Hotline',
                'category': 'domestic_violence',
                'description': '24/7 support for domestic violence victims',
                'phone_number': '1-800-799-7233',
                'website_url': 'https://www.thehotline.org',
                'is_24_7': True,
                'languages_supported': 'English, Spanish, 200+ languages',
                'is_verified': True
            },
            {
                'name': 'The Trevor Project',
                'category': 'lgbtq',
                'description': 'Crisis intervention and suicide prevention for LGBTQ youth',
                'phone_number': '1-866-488-7386',
                'website_url': 'https://www.thetrevorproject.org',
                'is_24_7': True,
                'languages_supported': 'English, Spanish',
                'is_verified': True
            }
        ]
        
        print("🌱 Seeding crisis resources...")
        for resource in crisis_resources:
            await conn.execute("""
                INSERT INTO crisis_resources (
                    name, category, description, phone_number, website_url, 
                    text_line, is_24_7, languages_supported, is_verified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT DO NOTHING
            """, 
                resource['name'], resource['category'], resource['description'],
                resource['phone_number'], resource['website_url'], resource.get('text_line'),
                resource['is_24_7'], resource['languages_supported'], resource['is_verified']
            )
        
        print(f"✅ Seeded {len(crisis_resources)} crisis resources")
        
        # Get a user to create sample data for
        user_id = await conn.fetchval("SELECT id FROM users LIMIT 1")
        if user_id:
            print(f"👤 Creating sample data for user: {user_id}")
            
            # Create sample emergency contact
            await conn.execute("""
                INSERT INTO emergency_contacts (
                    user_id, name, relationship, phone_number, priority_level, consent_obtained
                ) VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT DO NOTHING
            """, user_id, "Emergency Contact", "Friend", "+1234567890", 1, True)
            
            # Create sample safety plan
            await conn.execute("""
                INSERT INTO safety_plans (
                    user_id, plan_name, warning_signs, internal_coping_strategies,
                    reasons_for_living
                ) VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """, 
                user_id, 
                "My Safety Plan",
                ["Feeling overwhelmed", "Sleep problems"],
                ["Deep breathing", "Meditation"],
                ["Family", "Future goals"]
            )
            
            # Create sample wellness checkin
            await conn.execute("""
                INSERT INTO wellness_checkins (
                    user_id, checkin_date, mood_rating, anxiety_level, sleep_quality
                ) VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """, user_id, date.today(), 7, 3, 4)
            
            print("✅ Created sample user data")
        
        await conn.close()
        print("🎉 Crisis data seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding crisis data: {e}")

if __name__ == "__main__":
    asyncio.run(seed_crisis_data())
