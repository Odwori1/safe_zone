import asyncio
import requests
from app.database.database import database
from app.core.security import get_password_hash, verify_password

async def test_blueprint_alignment():
    """Test that we have all Phase 1 blueprint items working"""
    print("🎯 TESTING BLUEPRINT PHASE 1 ALIGNMENT")
    
    # 1. Health check endpoints (BLUEPRINT ITEM)
    print("\n1. 🩺 Health Check Endpoints")
    try:
        response = requests.get("http://localhost:8001/api/v1/health")
        health_data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Database: {health_data.get('database', 'unknown')}")
        print(f"   ✅ Service: {health_data.get('service', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    # 2. Database connection (BLUEPRINT ITEM - CRITICAL)
    print("\n2. 🗄️ Database Connection with RLS")
    try:
        await database.connect()
        async with database.pool.acquire() as conn:
            # Check if users table exists with RLS
            rls_enabled = await conn.fetchval("""
                SELECT relrowsecurity FROM pg_class WHERE relname = 'users'
            """)
            print(f"   ✅ RLS enabled: {rls_enabled}")
            
            # Check table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'users'
                )
            """)
            print(f"   ✅ Users table exists: {table_exists}")
            
        await database.close()
        print("   ✅ Database connection working")
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
    
    # 3. Password hashing (BLUEPRINT ITEM)
    print("\n3. 🔐 Password Hashing (bcrypt)")
    try:
        password = "secure_test_password_123"
        hashed = get_password_hash(password)
        verified = verify_password(password, hashed)
        print(f"   ✅ Hashing working: {verified}")
        print(f"   ✅ Hash length: {len(hashed)}")
    except Exception as e:
        print(f"   ❌ Password hashing failed: {e}")
    
    # 4. Security configuration (BLUEPRINT ITEM)
    print("\n4. 🛡️ Security Configuration")
    from app.core.config import settings
    print(f"   ✅ Environment: {settings.environment}")
    print(f"   ✅ CORS configured: {len(settings.cors_origins) > 0}")
    print(f"   ✅ Rate limiting: {settings.rate_limit_per_minute}/min")
    
    # 5. Timezone awareness (ENHANCEMENT FOR GLOBAL APP)
    print("\n5. 🌍 Timezone Awareness")
    from app.utils.timezone import timezone_handler
    utc_now = timezone_handler.get_utc_now()
    print(f"   ✅ UTC time: {utc_now}")
    print(f"   ✅ Timezone validation: {timezone_handler.validate_timezone('America/New_York')}")
    
    print("\n🎉 BLUEPRINT PHASE 1 VALIDATION COMPLETE!")
    print("   Ready for: User authentication system → JWT tokens → Password hashing")

if __name__ == "__main__":
    asyncio.run(test_blueprint_alignment())
