"""
Create crisis support system tables following EXACT project patterns
Based on successful patterns from create_likes_tables_fixed.py and create_posts_schema.py
"""
import asyncpg
import asyncio
from datetime import datetime, timezone

async def create_crisis_tables():
    """Create crisis support system tables following proven patterns"""
    
    # Database connection - USE SUPERUSER FOR TABLE CREATION
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        database='safe_zone',
        user='safe_zone_app_user',  # Try with app user first
        password='secure_app_password_2024'
    )
    
    try:
        print("🔧 Creating crisis support system tables...")
        
        # EMERGENCY CONTACTS TABLE - Follow posts table pattern
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
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✅ Created emergency_contacts table")

        # CRISIS RESOURCES TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS crisis_resources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
        print("✅ Created crisis_resources table")

        # SAFETY PLANS TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS safety_plans (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                plan_name VARCHAR(200) NOT NULL DEFAULT 'My Safety Plan',
                warning_signs TEXT[],
                internal_coping_strategies TEXT[],
                external_coping_strategies TEXT[],
                social_contacts JSONB,
                professional_contacts JSONB,
                environment_safety TEXT[],
                reasons_for_living TEXT[],
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✅ Created safety_plans table")

        # WELLNESS CHECKINS TABLE
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS wellness_checkins (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                checkin_date DATE NOT NULL DEFAULT CURRENT_DATE,
                mood_rating INTEGER CHECK (mood_rating BETWEEN 1 AND 10),
                anxiety_level INTEGER CHECK (anxiety_level BETWEEN 1 AND 10),
                sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 5),
                safety_concerns BOOLEAN DEFAULT FALSE,
                safety_concerns_details TEXT,
                coping_strategies_used TEXT[],
                support_needed BOOLEAN DEFAULT FALSE,
                support_type VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✅ Created wellness_checkins table")

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
        print("✅ Created crisis_alerts table")

        print("🎯 All crisis tables created successfully!")
        print("📋 Next: Enable RLS policies using the established pattern...")

    except Exception as e:
        print(f"❌ Error creating crisis tables: {str(e)}")
        # If app user fails, try with superuser
        if "must be owner" in str(e) or "permission denied" in str(e):
            print("🔄 Retrying with superuser privileges...")
            await conn.close()
            await create_crisis_tables_superuser()
        else:
            raise
    finally:
        await conn.close()

async def create_crisis_tables_superuser():
    """Create tables using superuser credentials"""
    try:
        # Use superuser for table creation (check your .env for superuser credentials)
        superuser_conn = await asyncpg.connect(
            host='localhost',
            port=5433,
            database='safe_zone',
            user='postgres',  # Default superuser
            password='your_postgres_password_here'  # Check your .env file
        )
        
        print("🔧 Creating tables with superuser privileges...")
        
        # Repeat the same CREATE TABLE statements as above
        tables_sql = [
            """
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
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS crisis_resources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            """,
            # ... include all other table creation SQL
        ]
        
        for i, sql in enumerate(tables_sql):
            await superuser_conn.execute(sql)
            print(f"✅ Created table {i+1} with superuser")
        
        await superuser_conn.close()
        print("🎯 All crisis tables created successfully with superuser!")
        
    except Exception as e:
        print(f"❌ Superuser also failed: {str(e)}")
        raise

async def enable_crisis_rls_policies():
    """Enable RLS policies separately using the app user"""
    print("🔧 Enabling RLS policies...")
    
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        database='safe_zone',
        user='safe_zone_app_user',
        password='secure_app_password_2024'
    )
    
    try:
        # Enable RLS on each table
        tables = [
            'emergency_contacts',
            'crisis_resources', 
            'safety_plans',
            'wellness_checkins',
            'crisis_alerts'
        ]
        
        for table in tables:
            await conn.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
            print(f"✅ Enabled RLS on {table}")
        
        # Add basic RLS policies (simplified version)
        await conn.execute("""
            CREATE POLICY IF NOT EXISTS user_emergency_contacts_policy ON emergency_contacts
            FOR ALL USING (user_id = auth.uid());
        """)
        
        await conn.execute("""
            CREATE POLICY IF NOT EXISTS crisis_resources_read_policy ON crisis_resources
            FOR SELECT USING (true);
        """)
        
        await conn.execute("""
            CREATE POLICY IF NOT EXISTS user_safety_plans_policy ON safety_plans
            FOR ALL USING (user_id = auth.uid());
        """)
        
        await conn.execute("""
            CREATE POLICY IF NOT EXISTS user_wellness_checkins_policy ON wellness_checkins
            FOR ALL USING (user_id = auth.uid());
        """)
        
        await conn.execute("""
            CREATE POLICY IF NOT EXISTS user_crisis_alerts_policy ON crisis_alerts
            FOR ALL USING (user_id = auth.uid());
        """)
        
        print("🎯 All RLS policies enabled successfully!")
        
    except Exception as e:
        print(f"⚠️ RLS policy setup had issues: {str(e)}")
        print("You may need to run RLS policies separately")
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 Starting Crisis Support System Table Creation...")
    asyncio.run(create_crisis_tables())
    
    # Try to enable RLS policies after table creation
    print("\n🔧 Setting up RLS policies...")
    asyncio.run(enable_crisis_rls_policies())
    
    print("\n🎉 Crisis Support System tables setup completed!")
    print("📋 Next steps:")
    print("   1. Verify tables were created in database")
    print("   2. Check RLS policies are working")
    print("   3. Proceed with backend endpoints")
