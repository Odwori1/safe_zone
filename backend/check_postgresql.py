import subprocess
import os

def check_postgresql():
    print("🔍 Checking PostgreSQL Status...")
    
    # Check 1: Service status
    print("1. Checking service status...")
    result = subprocess.run(['sudo', 'systemctl', 'status', 'postgresql'], 
                          capture_output=True, text=True)
    print(f"   Service: {result.returncode}")
    
    # Check 2: Process running
    print("2. Checking processes...")
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    postgres_processes = [line for line in result.stdout.split('\n') if 'postgres' in line and 'grep' not in line]
    print(f"   PostgreSQL processes: {len(postgres_processes)}")
    for proc in postgres_processes[:3]:  # Show first 3
        print(f"     {proc.split()[1]}: {proc.split()[10][:50]}...")
    
    # Check 3: Port listening
    print("3. Checking port 5432...")
    result = subprocess.run(['sudo', 'netstat', '-tlnp'], capture_output=True, text=True)
    port_listening = '5432' in result.stdout and 'postgres' in result.stdout
    print(f"   Port 5432 listening: {port_listening}")
    
    # Check 4: Direct connection
    print("4. Testing direct connection...")
    try:
        result = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', 'SELECT version();'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Direct connection successful")
            version_line = [line for line in result.stdout.split('\n') if 'PostgreSQL' in line][0]
            print(f"   {version_line}")
        else:
            print(f"   ❌ Direct connection failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Connection test error: {e}")
    
    return port_listening and len(postgres_processes) > 0

if __name__ == "__main__":
    print("🎯 PostgreSQL Diagnostic Check")
    print("=" * 50)
    
    postgres_ok = check_postgresql()
    
    print("\n" + "=" * 50)
    if postgres_ok:
        print("✅ PostgreSQL is running correctly")
        print("🚀 You can start the application server")
    else:
        print("❌ PostgreSQL is not running properly")
        print("\n💡 Try these commands:")
        print("   sudo systemctl start postgresql@14-main")
        print("   sudo pg_ctlcluster 14 main start")
        print("   sudo -u postgres /usr/lib/postgresql/14/bin/pg_ctl -D /var/lib/postgresql/14/main start")
