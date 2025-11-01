import asyncpg
import asyncio
import uuid
from datetime import datetime

async def add_uganda_resources():
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("Adding Uganda-specific crisis resources with RLS context...")
        
        # First, we need to temporarily disable RLS or use a superuser context
        # Since these are public resources, we'll use a different approach
        
        # Get an admin user ID to set as context (using the developer test user)
        user_result = await conn.fetchrow("SELECT id FROM users WHERE email = 'developer_test@example.com'")
        if not user_result:
            print("❌ Could not find admin user")
            return
            
        admin_user_id = user_result['id']
        print(f"Using admin user context: {admin_user_id}")
        
        # Set the user context for RLS
        await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(admin_user_id))
        
        # Uganda-specific crisis resources
        uganda_resources = [
            {
                'name': 'Butabika National Mental Referral Hospital',
                'description': 'Main psychiatric referral hospital providing comprehensive mental health services, inpatient and outpatient care, and community outreach programs.',
                'category': 'mental_health',
                'phone_number': '+256-414-505-500',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "lg", "sw"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': '["hospital", "inpatient", "outpatient", "kampala"]'
            },
            {
                'name': 'Uganda Police Emergency',
                'description': 'Emergency police services available 24/7 throughout Uganda.',
                'category': 'emergency',
                'phone_number': '999',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "sw", "lg"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': '["police", "emergency", "security"]'
            },
            {
                'name': 'Uganda Emergency Medical Services',
                'description': 'Ambulance and emergency medical services across Uganda.',
                'category': 'emergency',
                'phone_number': '112',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "sw"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': '["ambulance", "medical", "emergency"]'
            },
            {
                'name': 'Uganda Mental Health Helpline',
                'description': 'Free national helpline for mental health support and crisis intervention.',
                'category': 'crisis_support',
                'phone_number': '0800 200 600',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "lg", "sw"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': '["helpline", "free", "support"]'
            },
            {
                'name': 'Mental Health Uganda (MHU)',
                'description': 'Organization advocating for mental health awareness, support, and rights in Uganda.',
                'category': 'support_group',
                'phone_number': '+256-414-534-567',
                'website_url': 'https://mentalhealthuganda.org',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "lg"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': '["advocacy", "support", "awareness"]'
            },
            {
                'name': 'Mulago Hospital Psychiatry Department',
                'description': 'Psychiatric services department within Mulago National Referral Hospital.',
                'category': 'mental_health',
                'phone_number': '+256-414-541-541',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "lg"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': '["hospital", "psychiatry", "kampala"]'
            },
            {
                'name': 'Gulu Regional Referral Hospital Psychiatry Unit',
                'description': 'Mental health services for the Northern region of Uganda.',
                'category': 'mental_health',
                'phone_number': '+256-471-432-167',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "ach"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': '["hospital", "northern", "gulu"]'
            },
            {
                'name': 'Mbale Regional Referral Hospital Psychiatry',
                'description': 'Mental health services for Eastern Uganda region.',
                'category': 'mental_health',
                'phone_number': '+256-454-433-214',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "lumasaba"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': '["hospital", "eastern", "mbale"]'
            },
            {
                'name': 'Uganda Child Helpline',
                'description': 'National helpline for child protection and support services.',
                'category': 'support_group',
                'phone_number': '116',
                'website_url': '',
                'chat_url': '',
                'text_line': '',
                'languages': '["en", "lg", "sw"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 1,
                'tags': '["children", "helpline", "protection"]'
            },
            {
                'name': 'Ministry of Health Uganda',
                'description': 'Government ministry providing information on mental health policies and services nationwide.',
                'category': 'information',
                'phone_number': '+256-417-712-260',
                'website_url': 'https://www.health.go.ug',
                'chat_url': '',
                'text_line': '',
                'languages': '["en"]',
                'operating_hours': None,
                'geographic_scope': 'UG',
                'is_active': True,
                'priority': 2,
                'tags': '["government", "information", "policy"]'
            }
        ]
        
        # Check if resources already exist to avoid duplicates
        existing_resources = await conn.fetch("SELECT name FROM crisis_resources WHERE geographic_scope = 'UG'")
        existing_names = [r['name'] for r in existing_resources]
        
        resources_added = 0
        for resource in uganda_resources:
            if resource['name'] in existing_names:
                print(f"⚠️ Resource already exists: {resource['name']}")
                continue
                
            await conn.execute('''
                INSERT INTO crisis_resources (
                    id, name, description, category, phone_number, website_url, chat_url,
                    text_line, languages, operating_hours, geographic_scope, is_active,
                    priority, tags, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
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
            resources_added += 1
            print(f"✅ Added: {resource['name']}")
        
        print(f"🎉 Successfully added {resources_added} Uganda-specific crisis resources")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error adding Uganda resources: {e}")
        import traceback
        traceback.print_exc()

# Run the script
asyncio.run(add_uganda_resources())
