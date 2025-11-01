import asyncpg
import asyncio
import uuid
import json
from datetime import datetime

async def add_uganda_resources_fixed_json():
    """Add Uganda resources with proper JSON formatting for languages and tags"""
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("🔄 Adding Uganda resources with proper JSON formatting...")
        
        # Uganda resources - convert lists to JSON strings
        uganda_resources = [
            {
                'name': 'Uganda Police Emergency',
                'description': 'Emergency police services available throughout Uganda. Call 999 or 112 for immediate assistance.',
                'category': 'emergency',
                'phone_number': '999',
                'website_url': '',
                'chat_url': '', 
                'text_line': '',
                'languages': json.dumps(["en", "sw"]),  # Convert to JSON string
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': json.dumps(["police", "emergency", "security", "uganda"])  # Convert to JSON string
            },
            {
                'name': 'Uganda Mental Health Helpline',
                'description': 'Free national helpline for mental health support and crisis intervention. Available 24/7.',
                'category': 'crisis_support', 
                'phone_number': '0800 200 600',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "lg", "sw"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': json.dumps(["helpline", "free", "support", "uganda", "mental health"])
            },
            {
                'name': 'Butabika National Mental Referral Hospital',
                'description': 'Main psychiatric referral hospital providing comprehensive mental health services, inpatient and outpatient care, and community outreach programs.',
                'category': 'mental_health',
                'phone_number': '+256-414-505-500',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "lg", "sw"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': json.dumps(["hospital", "inpatient", "outpatient", "kampala", "uganda"])
            },
            {
                'name': 'Uganda Emergency Medical Services',
                'description': 'Ambulance and emergency medical services across Uganda.',
                'category': 'emergency',
                'phone_number': '112',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "sw"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': json.dumps(["ambulance", "medical", "emergency", "uganda"])
            },
            {
                'name': 'Mental Health Uganda (MHU)',
                'description': 'Organization advocating for mental health awareness, support, and rights in Uganda.',
                'category': 'support_group',
                'phone_number': '+256-414-534-567',
                'website_url': 'https://mentalhealthuganda.org',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "lg"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': json.dumps(["advocacy", "support", "awareness", "uganda"])
            },
            {
                'name': 'Mulago Hospital Psychiatry Department',
                'description': 'Psychiatric services department within Mulago National Referral Hospital.',
                'category': 'mental_health',
                'phone_number': '+256-414-541-541',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "lg"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': json.dumps(["hospital", "psychiatry", "kampala", "uganda"])
            },
            {
                'name': 'Gulu Regional Referral Hospital Psychiatry Unit',
                'description': 'Mental health services for the Northern region of Uganda.',
                'category': 'mental_health',
                'phone_number': '+256-471-432-167',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "ach"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': json.dumps(["hospital", "northern", "gulu", "uganda"])
            },
            {
                'name': 'Mbale Regional Referral Hospital Psychiatry',
                'description': 'Mental health services for Eastern Uganda region.',
                'category': 'mental_health',
                'phone_number': '+256-454-433-214',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "lumasaba"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': json.dumps(["hospital", "eastern", "mbale", "uganda"])
            },
            {
                'name': 'Uganda Child Helpline',
                'description': 'National helpline for child protection and support services.',
                'category': 'support_group',
                'phone_number': '116',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en", "lg", "sw"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': json.dumps(["children", "helpline", "protection", "uganda"])
            },
            {
                'name': 'Ministry of Health Uganda',
                'description': 'Government ministry providing information on mental health policies and services nationwide.',
                'category': 'information',
                'phone_number': '+256-417-712-260',
                'website_url': 'https://www.health.go.ug',
                'chat_url': '',
                'text_line': '',
                'languages': json.dumps(["en"]),
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': json.dumps(["government", "information", "policy", "uganda"])
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
                
                # Insert the resource with proper JSON strings
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
                    resource['languages'],  # Now JSON string
                    resource['operating_hours'],
                    resource['geographic_scope'],
                    resource['is_active'],
                    resource['priority'],
                    resource['tags'],  # Now JSON string
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

asyncio.run(add_uganda_resources_fixed_json())
