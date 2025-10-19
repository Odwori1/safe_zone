import socket

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False

print("🔍 Checking PostgreSQL Port Availability")
print("=" * 40)

ports_to_check = [5432, 5433, 5434, 5435, 5436, 5437, 5438, 5439, 5440]

available_ports = []
for port in ports_to_check:
    if check_port(port):
        available_ports.append(port)
        print(f"✅ Port {port}: AVAILABLE")
    else:
        print(f"❌ Port {port}: IN USE")

print("\n" + "=" * 40)
if available_ports:
    print(f"🎯 Available ports: {available_ports}")
    print(f"💡 Recommended: Use port {available_ports[0]} for PostgreSQL")
else:
    print("❌ No available ports in range 5432-5440")
    print("💡 Try ports 5441-5450 instead")
