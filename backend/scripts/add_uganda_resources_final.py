import asyncpg
import asyncio
import uuid
from datetime import datetime

async def add_uganda_resources_final():
    """Add Uganda resources now that INSERT policy is fixed"""
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("🔄 Adding Uganda resources with proper INSERT policy...")
        
        # Uganda resources
        uganda_resources = [
            {
                'name': 'Uganda Police Emergency',
                'description': 'Emergency police services available throughout Uganda. Call 999 or 112 for immediate assistance.',
                'category': 'emergency',
                'phone_number': '999',
                'website_url': '',
                'chat_url': '', 
                'text_line': '',
                'languages': ["en", "sw"],
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': ["police", "emergency", "security", "uganda"]
            },
            {
                'name': 'Uganda Mental Health Helpline',
                'description': 'Free national helpline for mental health support and crisis intervention. Available 24/7.',
                'category': 'crisis_support', 
                'phone_number': '0800 200 600',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': ["en", "lg", "sw"],
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': ["helpline", "free", "support", "uganda", "mental health"]
            },
            {
                'name': 'Butabika National Mental Referral Hospital',
                'description': 'Main psychiatric referral hospital providing comprehensive mental health services, inpatient and outpatient care, and community outreach programs.',
                'category': 'mental_health',
                'phone_number': '+256-414-505-500',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': ["en", "lg", "sw"],
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': ["hospital", "inpatient", "outpatient", "kampala", "uganda"]
            },
            {
                'name': 'Uganda Emergency Medical Services',
                'description': 'Ambulance and emergency medical services across Uganda.',
                'category': 'emergency',
                'phone_number': '112',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': ["en", "sw"],
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': ["ambulance", "medical", "emergency", "uganda"]
            },
            {
                'name': 'Mental Health Uganda (MHU)',
                'description': 'Organization advocating for mental health awareness, support, and rights in Uganda.',
                'category': 'support_group',
                'phone_number': '+256-414-534-567',
                'website_url': 'https://mentalhealthuganda.org',
                'chat_url': '',
                'text_line': '',
                'languages': ["en", "lg"],
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': ["advocacy", "support", "awareness", "uganda"]
            }
        ]
        
        resources_added = 0
        for resource in uganda_resources:
            try:
                # Check if already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM crisis_resources WHERE name = $1 AND geographic_scope = 'UG'",
                    resource['name']
                )
                
                if existing:
                    print(f"⚠️ Already exists: {resource['name']}")
                    continue
                
                # Insert the resource
                result = await conn.fetchrow('''
                    INSERT INTO crisis_resources 
                    (id, name, description, category, phone_number, website_url, chat_url, 
                     text_line, languages, operating_hours, geographic_scope, is_active, 
                     priority, tags, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    RETURNING id
                ''',
                    str(uuid.uuid4()),
                    resource['name'],
                    resource['description'],
                    resource['category'], 
                    resource['phone_number'],
                    resource['website_url'],
                    resource['chat_url'],
                    resource['text_line'],
                    resource['languages'],
                    resource['operating_hours'],
                    resource['geographic_scope'],
                    resource['is_active'],
                    resource['priority'],
                    resource['tags'],
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                
                if result:
                    resources_added += 1
                    print(f"✅ Added: {resource['name']}")
                else:
                    print(f"❌ Failed: {resource['name']}")
                    
            except Exception as e:
                print(f"❌ Error adding {resource['name']}: {e}")
                continue
        
        print(f"🎉 Successfully added {resources_added} Uganda resources")
        
        # Verify total Uganda resources
        ug_resources = await conn.fetch("SELECT name FROM crisis_resources WHERE geographic_scope = 'UG'")
        print(f"📋 Total Uganda resources in database: {len(ug_resources)}")
        for res in ug_resources:
            print(f"  - {res['name']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Overall error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(add_uganda_resources_final())
