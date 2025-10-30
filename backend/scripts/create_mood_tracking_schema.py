#!/usr/bin/env python3
"""
Enhanced Mood Tracking Schema
Hybrid system integrating with posts/journals + standalone entries
"""

import asyncpg
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_mood_tracking_schema():
    """Create enhanced mood tracking tables"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Creating enhanced mood tracking schema...")
        
        # Enhanced mood_entries table for standalone and integrated tracking
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mood_entries (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                
                -- Core mood data
                mood_type VARCHAR(50) NOT NULL,
                intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),
                
                -- Context and integration
                source_type VARCHAR(20) DEFAULT 'standalone', -- 'post', 'journal', 'standalone'
                source_id UUID, -- post_id or journal_id when integrated
                
                -- Extended tracking fields
                triggers TEXT[] DEFAULT '{}',
                activities TEXT[] DEFAULT '{}',
                physical_symptoms TEXT[] DEFAULT '{}',
                social_context VARCHAR(50), -- 'alone', 'friends', 'family', 'colleagues'
                sleep_quality INTEGER CHECK (sleep_quality >= 1 AND sleep_quality <= 10),
                energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
                location VARCHAR(100),
                weather VARCHAR(50),
                
                -- Duration tracking
                duration_minutes INTEGER,
                
                -- Medication tracking
                medication_taken BOOLEAN DEFAULT false,
                medication_notes TEXT,
                
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                
                CONSTRAINT valid_source_type CHECK (source_type IN ('post', 'journal', 'standalone'))
            );
        """)
        
        # Mood patterns and insights table (for AI later)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mood_insights (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                insight_type VARCHAR(50) NOT NULL,
                pattern_description TEXT NOT NULL,
                confidence_score DECIMAL(3,2) DEFAULT 0.0,
                data_points INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Enable RLS
        await conn.execute("ALTER TABLE mood_entries ENABLE ROW LEVEL SECURITY;")
        await conn.execute("ALTER TABLE mood_insights ENABLE ROW LEVEL SECURITY;")
        
        # Create RLS policies
        await conn.execute("""
            CREATE POLICY mood_entries_user_policy ON mood_entries
            FOR ALL USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        await conn.execute("""
            CREATE POLICY mood_insights_user_policy ON mood_insights
            FOR ALL USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX idx_mood_entries_user_date ON mood_entries(user_id, created_at);")
        await conn.execute("CREATE INDEX idx_mood_entries_source ON mood_entries(source_type, source_id);")
        await conn.execute("CREATE INDEX idx_mood_entries_mood_type ON mood_entries(mood_type);")
        await conn.execute("CREATE INDEX idx_mood_insights_user ON mood_insights(user_id, insight_type);")
        
        print("✅ Enhanced mood tracking schema created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating mood tracking schema: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_mood_tracking_schema())
