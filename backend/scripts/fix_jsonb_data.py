#!/usr/bin/env python3
"""
Fix the JSONB data in crisis_resources table
The columns are JSONB but contain JSON strings instead of proper JSON objects
"""
import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_jsonb_data():
    """Fix JSONB columns that contain JSON strings instead of proper JSON"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        print("🔧 Fixing JSONB data in crisis_resources...")
        
        # Get all crisis resources to check current data
        resources = await conn.fetch("SELECT id, name, languages, tags FROM crisis_resources")
        
        print(f"📊 Found {len(resources)} resources to check")
        
        fixed_count = 0
        for resource in resources:
            resource_id = resource['id']
            resource_name = resource['name']
            needs_fix = False
            updates = {}
            
            # Check languages column
            languages = resource['languages']
            if languages and isinstance(languages, str):
                print(f"🔄 Fixing languages for: {resource_name}")
                try:
                    # Parse the JSON string to get the actual list
                    parsed_languages = json.loads(languages)
                    updates['languages'] = parsed_languages
                    needs_fix = True
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse languages for {resource_name}: {e}")
                    # Set to default if parsing fails
                    updates['languages'] = ['en']
                    needs_fix = True
            
            # Check tags column
            tags = resource['tags']
            if tags and isinstance(tags, str):
                print(f"🔄 Fixing tags for: {resource_name}")
                try:
                    # Parse the JSON string to get the actual list
                    parsed_tags = json.loads(tags)
                    updates['tags'] = parsed_tags
                    needs_fix = True
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse tags for {resource_name}: {e}")
                    # Set to empty list if parsing fails
                    updates['tags'] = []
                    needs_fix = True
            
            # Update the record if fixes are needed
            if needs_fix:
                try:
                    # Build the update query
                    set_clauses = []
                    values = []
                    param_count = 1
                    
                    for field, value in updates.items():
                        set_clauses.append(f"{field} = ${param_count}")
                        values.append(value)
                        param_count += 1
                    
                    values.append(resource_id)
                    query = f"""
                        UPDATE crisis_resources 
                        SET {', '.join(set_clauses)}
                        WHERE id = ${param_count}
                    """
                    
                    await conn.execute(query, *values)
                    fixed_count += 1
                    print(f"✅ Fixed: {resource_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to update {resource_name}: {e}")
        
        print(f"\n🎉 Fixed {fixed_count} resources")
        
        # Verify the fixes
        print("\n🔍 Verifying fixes...")
        test_resources = await conn.fetch("SELECT id, name, languages, tags FROM crisis_resources LIMIT 3")
        for resource in test_resources:
            print(f"\n📋 {resource['name']}:")
            print(f"   Languages: {resource['languages']} (type: {type(resource['languages']).__name__})")
            print(f"   Tags: {resource['tags']} (type: {type(resource['tags']).__name__})")
        
        await conn.close()
        print("\n🎉 JSONB data fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing JSONB data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_jsonb_data())
