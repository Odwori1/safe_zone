import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_both_ports():
    print("🔍 Testing PostgreSQL Connection on Both Ports")
    print("=" * 50)
    
    for port in [5432, 5433]:
        print(f"\nTesting port {port}...")
        try:
            conn = await asyncpg.connect(
                host=os.getenv('DB_HOST', '127.0.0.1'),
                port=port,
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            version = await conn.fetchval("SELECT version();")
            print(f"✅ SUCCESS on port {port}")
            print(f"   PostgreSQL: {version.split(',')[0]}")
            await conn.close()
            
            # Update .env with working port
            with open('.env', 'r') as f:
                content = f.read()
            content = content.replace(f"DB_PORT={os.getenv('DB_PORT')}", f"DB_PORT={port}")
            with open('.env', 'w') as f:
                f.write(content)
            print(f"   ✅ Updated .env to use port {port}")
            return True
            
        except Exception as e:
            print(f"❌ FAILED on port {port}: {e}")
    
    return False

async def main():
    success = await test_both_ports()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 PostgreSQL connection established!")
        print("🚀 You can now start the server")
    else:
        print("❌ Could not connect to PostgreSQL on either port")
        print("💡 Check if PostgreSQL is running: sudo systemctl status postgresql@14-main")

asyncio.run(main())
