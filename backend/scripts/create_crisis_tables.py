"""
Create crisis support system tables following EXACT project patterns
"""
import asyncpg
import asyncio
from datetime import datetime, timezone

async def create_crisis_tables():
    """Create crisis support system tables with RLS policies"""
    
    # Database connection - USE EXISTING CREDENTIALS
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        database='safe_zone',
        user='safe_zone_app_user',
        password='secure_app_password_2024'
    )
    
    try:
        # EMERGENCY CONTACTS TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                relationship VARCHAR(100) NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                email VARCHAR(255),
                priority_level INTEGER NOT NULL DEFAULT 3 CHECK (priority_level BETWEEN 1 AND 3),
                is_verified BOOLEAN DEFAULT FALSE,
                consent_obtained BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                
                UNIQUE(user_id, phone_number)
            );
        """)
        
        # Enable RLS on emergency_contacts
        await conn.execute("""
            ALTER TABLE emergency_contacts ENABLE ROW LEVEL SECURITY;
        """)
        
        # RLS Policy: Users can only access their own contacts
        await conn.execute("""
            CREATE POLICY user_emergency_contacts_policy ON emergency_contacts
            FOR ALL USING (user_id = auth.uid());
        """)
        
        # CRISIS RESOURCES TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS crisis_resources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuiduid(),
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT,
                phone_number VARCHAR(20),
                website_url VARCHAR(500),
                email VARCHAR(255),
                address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                country VARCHAR(100) DEFAULT 'US',
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                is_24_7 BOOLEAN DEFAULT FALSE,
                languages_supported VARCHAR(500),
                special_notes TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                created_by UUID REFERENCES users(id),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Enable RLS on crisis_resources
        await conn.execute("""
            ALTER TABLE crisis_resources ENABLE ROW LEVEL SECURITY;
        """)
        
        # RLS Policy: All authenticated users can read crisis resources
        await conn.execute("""
            CREATE POLICY crisis_resources_read_policy ON crisis_resources
            FOR SELECT USING (true);
        """)
        
        # Only admins can modify crisis resources
        await conn.execute("""
            CREATE POLICY crisis_resources_modify_policy ON crisis_resources
            FOR ALL USING (created_by = auth.uid());
        """)
        
        # SAFETY PLANS TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS safety_plans (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                plan_name VARCHAR(200) NOT NULL DEFAULT 'My Safety Plan',
                
                -- Warning Signs
                warning_signs TEXT[],
                
                -- Coping Strategies
                internal_coping_strategies TEXT[],
                external_coping_strategies TEXT[],
                
                -- Social Contacts
                social_contacts JSONB,
                
                -- Professional Contacts
                professional_contacts JSONB,
                
                -- Environment Safety
                environment_safety TEXT[],
                
                -- Reasons for Living
                reasons_for_living TEXT[],
                
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                
                UNIQUE(user_id, plan_name)
            );
        """)
        
        # Enable RLS on safety_plans
        await conn.execute("""
            ALTER TABLE safety_plans ENABLE ROW LEVEL SECURITY;
        """)
        
        # RLS Policy: Users can only access their own safety plans
        await conn.execute("""
            CREATE POLICY user_safety_plans_policy ON safety_plans
            FOR ALL USING (user_id = auth.uid());
        """)
        
        # WELLNESS CHECKINS TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS wellness_checkins (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                checkin_date DATE NOT NULL DEFAULT CURRENT_DATE,
                
                -- Mood and wellbeing
                mood_rating INTEGER CHECK (mood_rating BETWEEN 1 AND 10),
                anxiety_level INTEGER CHECK (anxiety_level BETWEEN 1 AND 10),
                sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 5),
                
                -- Safety assessment
                safety_concerns BOOLEAN DEFAULT FALSE,
                safety_concerns_details TEXT,
                
                -- Coping strategies used
                coping_strategies_used TEXT[],
                
                -- Support needed
                support_needed BOOLEAN DEFAULT FALSE,
                support_type VARCHAR(100),
                
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                
                UNIQUE(user_id, checkin_date)
            );
        """)
        
        # Enable RLS on wellness_checkins
        await conn.execute("""
            ALTER TABLE wellness_checkins ENABLE ROW LEVEL SECURITY;
        """)
        
        # RLS Policy: Users can only access their own checkins
        await conn.execute("""
            CREATE POLICY user_wellness_checkins_policy ON wellness_checkins
            FOR ALL USING (user_id = auth.uid());
        """)
        
        # CRISIS ALERTS TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS crisis_alerts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('sos', 'wellness_check', 'safety_concern')),
                severity_level VARCHAR(20) NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
                message TEXT,
                location_data JSONB,
                is_resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMPTZ,
                resolved_by UUID REFERENCES users(id),
                resolution_notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Enable RLS on crisis_alerts
        await conn.execute("""
            ALTER TABLE crisis_alerts ENABLE ROW LEVEL SECURITY;
        """)
        
        # RLS Policy: Users can only access their own alerts
        await conn.execute("""
            CREATE POLICY user_crisis_alerts_policy ON crisis_alerts
            FOR ALL USING (user_id = auth.uid());
        """)
        
        print("✅ Crisis support system tables created successfully!")
        print("📋 Tables created:")
        print("   - emergency_contacts")
        print("   - crisis_resources") 
        print("   - safety_plans")
        print("   - wellness_checkins")
        print("   - crisis_alerts")
        
    except Exception as e:
        print(f"❌ Error creating crisis tables: {str(e)}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_crisis_tables())
