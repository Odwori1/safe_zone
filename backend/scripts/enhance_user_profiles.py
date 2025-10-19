#!/usr/bin/env python3
"""
Enhance user profiles for Seeker/Helper modes as per blueprint
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def enhance_user_profiles():
    """Add profile fields for Seeker/Helper modes"""
    try:
        await database.connect()
        print("✅ Database connected")
        
        async with database.pool.acquire() as conn:
            # Add profile columns for Seeker/Helper modes
            print("🔄 Enhancing user profiles for Seeker/Helper modes...")
            
            # Bio field for both Seekers and Helpers
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN bio TEXT;")
                print("✅ Added bio column")
            except Exception as e:
                print(f"⚠️ bio column: {e}")
            
            # Profile picture URL
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500);")
                print("✅ Added profile_picture column")
            except Exception as e:
                print(f"⚠️ profile_picture column: {e}")
            
            # Helper-specific fields (for mental health professionals/volunteers)
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN is_helper BOOLEAN DEFAULT false;")
                print("✅ Added is_helper column")
            except Exception as e:
                print(f"⚠️ is_helper column: {e}")
            
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN helper_credentials TEXT;")
                print("✅ Added helper_credentials column")
            except Exception as e:
                print(f"⚠️ helper_credentials column: {e}")
            
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN helper_specialties VARCHAR(500);")
                print("✅ Added helper_specialties column")
            except Exception as e:
                print(f"⚠️ helper_specialties column: {e}")
            
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN helper_verification_status VARCHAR(50) DEFAULT 'not_applied';")
                print("✅ Added helper_verification_status column")
            except Exception as e:
                print(f"⚠️ helper_verification_status column: {e}")
            
            # Seeker-specific fields (for those seeking support)
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN seeker_preferences JSONB DEFAULT '{}';")
                print("✅ Added seeker_preferences column")
            except Exception as e:
                print(f"⚠️ seeker_preferences column: {e}")
            
            # Update existing users to have default role-based settings
            print("🔄 Setting default profile values...")
            await conn.execute("""
                UPDATE users 
                SET is_helper = (role = 'helper'),
                    helper_verification_status = 
                        CASE 
                            WHEN role = 'helper' THEN 'pending' 
                            ELSE 'not_applied' 
                        END
                WHERE is_helper IS NULL OR helper_verification_status IS NULL;
            """)
            print("✅ Set default profile values")
            
            # Verify the enhanced structure
            print("\n📋 Enhanced user profiles structure:")
            columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position;
            """)
            
            profile_columns = [col for col in columns if col['column_name'] in 
                             ['bio', 'profile_picture', 'is_helper', 'helper_credentials', 
                              'helper_specialties', 'helper_verification_status', 'seeker_preferences']]
            
            for col in profile_columns:
                print(f"   - {col['column_name']} ({col['data_type']})")
            
        print("🎉 User profiles enhanced for Seeker/Helper modes!")
        
    except Exception as e:
        print(f"❌ Profile enhancement failed: {e}")
        raise
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(enhance_user_profiles())
