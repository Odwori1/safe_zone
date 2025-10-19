import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def init_database():
    # Database connection details
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'safe_zone_user'),
        'password': os.getenv('DB_PASSWORD', 'safe_zone_password_2024'),
        'database': os.getenv('DB_NAME', 'safe_zone')
    }
    
    try:
        # Connect to database
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to PostgreSQL database")
        
        # Enable extensions
        await conn.execute('''
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            CREATE EXTENSION IF NOT EXISTS "pgcrypto";
        ''')
        print("✅ Extensions enabled")
        
        # Create users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                username VARCHAR(50) UNIQUE NOT NULL CHECK (length(username) >= 3),
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                user_type VARCHAR(20) DEFAULT 'seeker' CHECK (user_type IN ('seeker', 'helper')),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        ''')
        print("✅ Users table created")
        
        # Create posts table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL CHECK (length(content) BETWEEN 1 AND 2000),
                content_type VARCHAR(20) DEFAULT 'text' CHECK (content_type IN ('text', 'audio', 'video')),
                tags TEXT[] DEFAULT '{}',
                is_public BOOLEAN DEFAULT true,
                requires_moderation BOOLEAN DEFAULT true,
                moderation_status VARCHAR(20) DEFAULT 'pending' CHECK (moderation_status IN ('pending', 'approved', 'rejected')),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        ''')
        print("✅ Posts table created")
        
        # Create journals table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS journals (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                mood VARCHAR(20) CHECK (mood IN ('happy', 'sad', 'anxious', 'angry', 'peaceful', 'tired', 'excited')),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        ''')
        print("✅ Journals table created")
        
        # Create indexes for performance
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
            CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_journals_user_id ON journals(user_id);
        ''')
        print("✅ Indexes created")
        
        await conn.close()
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
