#!/usr/bin/env python3
"""
Script to create crisis_resources and emergency_contacts tables with RLS
Phase 2, Item 8: Crisis Resources Integration
"""

import asyncpg
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

async def create_crisis_resources_schema():
    """Create crisis resources tables with RLS policies"""
    
    conn = None
    try:
        # Connect to PostgreSQL
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        # Enable UUID extension if not already enabled
        print("📦 Enabling UUID extension...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
        # Create crisis_resources table (admin-managed, global resources)
        print("🗂️ Creating crisis_resources table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS crisis_resources (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(100) NOT NULL,
                phone_number VARCHAR(50),
                website_url VARCHAR(500),
                chat_url VARCHAR(500),
                text_line VARCHAR(50),
                languages JSONB DEFAULT '["en"]',
                operating_hours JSONB,
                geographic_scope VARCHAR(100) DEFAULT 'global',
                is_active BOOLEAN DEFAULT true,
                priority INTEGER DEFAULT 1,
                tags JSONB DEFAULT '[]',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Create emergency_contacts table (user-specific emergency contacts)
        print("🗂️ Creating emergency_contacts table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(200) NOT NULL,
                relationship VARCHAR(100),
                phone_number VARCHAR(50) NOT NULL,
                email VARCHAR(200),
                is_primary BOOLEAN DEFAULT false,
                can_receive_alerts BOOLEAN DEFAULT false,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Create user_crisis_preferences table
        print("🗂️ Creating user_crisis_preferences table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_crisis_preferences (
                user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                preferred_language VARCHAR(10) DEFAULT 'en',
                country_code VARCHAR(5),
                emergency_contact_instructions TEXT,
                medical_information TEXT,
                consent_to_contact BOOLEAN DEFAULT false,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Enable Row Level Security on user-specific tables
        print("🔒 Enabling RLS on emergency_contacts...")
        await conn.execute("ALTER TABLE emergency_contacts ENABLE ROW LEVEL SECURITY;")
        
        print("🔒 Enabling RLS on user_crisis_preferences...")
        await conn.execute("ALTER TABLE user_crisis_preferences ENABLE ROW LEVEL SECURITY;")
        
        # crisis_resources is global (no RLS) - accessible to all users
        
        # Create RLS policies for user-specific tables
        print("📝 Creating RLS policies...")
        
        # Policy: Users can only view their own emergency contacts
        await conn.execute("""
            CREATE POLICY user_view_own_emergency_contacts ON emergency_contacts
            FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only insert their own emergency contacts
        await conn.execute("""
            CREATE POLICY user_insert_own_emergency_contacts ON emergency_contacts
            FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only update their own emergency contacts
        await conn.execute("""
            CREATE POLICY user_update_own_emergency_contacts ON emergency_contacts
            FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only delete their own emergency contacts
        await conn.execute("""
            CREATE POLICY user_delete_own_emergency_contacts ON emergency_contacts
            FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only view their own crisis preferences
        await conn.execute("""
            CREATE POLICY user_view_own_crisis_preferences ON user_crisis_preferences
            FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only insert their own crisis preferences
        await conn.execute("""
            CREATE POLICY user_insert_own_crisis_preferences ON user_crisis_preferences
            FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only update their own crisis preferences
        await conn.execute("""
            CREATE POLICY user_update_own_crisis_preferences ON user_crisis_preferences
            FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Create indexes for better performance
        print("📊 Creating indexes...")
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_crisis_resources_category ON crisis_resources(category);
            CREATE INDEX IF NOT EXISTS idx_crisis_resources_active ON crisis_resources(is_active);
            CREATE INDEX IF NOT EXISTS idx_crisis_resources_priority ON crisis_resources(priority);
            CREATE INDEX IF NOT EXISTS idx_emergency_contacts_user_id ON emergency_contacts(user_id);
            CREATE INDEX IF NOT EXISTS idx_emergency_contacts_primary ON emergency_contacts(is_primary);
        """)
        
        # Insert some sample crisis resources (global helplines)
        print("🌍 Inserting sample crisis resources...")
        sample_resources = [
            {
                'name': 'National Suicide Prevention Lifeline',
                'description': '24/7 free and confidential support for people in distress',
                'category': 'suicide_prevention',
                'phone_number': '1-800-273-8255',
                'website_url': 'https://suicidepreventionlifeline.org',
                'chat_url': 'https://suicidepreventionlifeline.org/chat/',
                'languages': '["en", "es"]',
                'geographic_scope': 'US'
            },
            {
                'name': 'Crisis Text Line',
                'description': 'Free 24/7 support for those in crisis. Text from anywhere in the US',
                'category': 'crisis_support',
                'phone_number': '',
                'text_line': 'HOME to 741741',
                'website_url': 'https://www.crisistextline.org',
                'chat_url': 'https://www.crisistextline.org/text-us/',
                'languages': '["en"]',
                'geographic_scope': 'US'
            },
            {
                'name': 'International Association for Suicide Prevention',
                'description': 'Global resources for suicide prevention',
                'category': 'information',
                'website_url': 'https://www.iasp.info/resources/Crisis_Centres/',
                'languages': '["en"]',
                'geographic_scope': 'global'
            },
            {
                'name': 'Emergency Services',
                'description': 'Local emergency services',
                'category': 'emergency',
                'phone_number': '911',
                'geographic_scope': 'US'
            }
        ]
        
        for resource in sample_resources:
            await conn.execute("""
                INSERT INTO crisis_resources 
                (name, description, category, phone_number, website_url, chat_url, text_line, languages, geographic_scope)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT DO NOTHING;
            """, 
            resource['name'], resource['description'], resource['category'],
            resource.get('phone_number', ''), resource.get('website_url', ''),
            resource.get('chat_url', ''), resource.get('text_line', ''),
            resource.get('languages', '["en"]'), resource.get('geographic_scope', 'global')
            )
        
        print("✅ Crisis resources schema created successfully!")
        print("   - crisis_resources table created (global resources)")
        print("   - emergency_contacts table created (user-specific)")
        print("   - user_crisis_preferences table created")
        print("   - RLS enabled with user isolation policies")
        print("   - Performance indexes created")
        print("   - Sample crisis resources inserted")
        
    except Exception as e:
        print(f"❌ Error creating crisis resources schema: {e}")
        raise
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(create_crisis_resources_schema())
