import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_actual_data():
    # Use the same connection settings as the app
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "5433"))
    db_name = os.getenv("DB_NAME", "safe_zone")
    db_user = os.getenv("DB_USER", "safe_zone_app_user")
    db_password = os.getenv("DB_PASSWORD", "secure_app_password_2024")
    
    print(f"🔗 Connecting to: {db_host}:{db_port}/{db_name} as {db_user}")
    
    conn = await asyncpg.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    
    print("🔍 Checking ACTUAL crisis resources data in database:")
    print("=" * 60)
    
    resources = await conn.fetch("""
        SELECT id, name, geographic_scope, category, phone_number
        FROM crisis_resources 
        ORDER BY name;
    """)
    
    for i, resource in enumerate(resources, 1):
        print(f"Resource {i}:")
        print(f"  Name: {resource['name']}")
        print(f"  Geographic Scope: '{resource['geographic_scope']}'")
        print(f"  Category: {resource['category']}")
        print(f"  Phone: {resource['phone_number']}")
        print("---")
    
    # Check specifically for invalid geographic_scope values
    print("\n🔍 Checking for INVALID geographic_scope values:")
    invalid_resources = await conn.fetch("""
        SELECT id, name, geographic_scope 
        FROM crisis_resources 
        WHERE geographic_scope NOT IN ('global', 'US', 'europe', 'asia', 'africa', 'local');
    """)
    
    if invalid_resources:
        print("❌ Found invalid geographic_scope values:")
        for resource in invalid_resources:
            print(f"  - {resource['name']}: '{resource['geographic_scope']}'")
    else:
        print("✅ All geographic_scope values are valid")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_actual_data())
