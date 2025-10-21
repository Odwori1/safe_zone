from app.core.config import settings

print("🔍 DATABASE CONNECTION DETAILS:")
print(f"Host: {settings.db_host}")
print(f"Port: {settings.db_port}") 
print(f"Database: {settings.db_name}")
print(f"User: {settings.db_user}")
print(f"Password: {'*' * len(settings.db_password)}")
print(f"Full URL: {settings.database_url}")
