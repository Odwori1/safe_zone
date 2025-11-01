#!/usr/bin/env python3
"""
Fix crisis data validation issues
"""
import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_crisis_data_validation():
    """Fix data validation issues in crisis resources"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Fix crisis_resources data
        print("🔧 Fixing crisis_resources data...")
        
        # Get all crisis resources
        resources = await conn.fetch("SELECT * FROM crisis_resources")
        
        for resource in resources:
            resource_id = resource['id']
            fixes = {}
            
            # Fix languages field
            if resource['languages'] and isinstance(resource['languages'], str):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(resource['languages'])
                    if isinstance(parsed, list):
                        fixes['languages'] = parsed
                    else:
                        fixes['languages'] = ['en']  # default
                except:
                    fixes['languages'] = ['en']  # default
            
            # Fix tags field  
            if resource['tags'] and isinstance(resource['tags'], str):
                try:
                    parsed = json.loads(resource['tags'])
                    if isinstance(parsed, list):
                        fixes['tags'] = parsed
                    else:
                        fixes['tags'] = []
                except:
                    fixes['tags'] = []
            
            # Update the record if fixes are needed
            if fixes:
                set_clauses = []
                values = []
                param_count = 1
                
                for field, value in fixes.items():
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
                print(f"✅ Fixed resource: {resource['name']}")
        
        print(f"✅ Fixed {len(resources)} crisis resources")
        
        await conn.close()
        print("🎉 Crisis data validation fixes completed!")
        
    except Exception as e:
        print(f"❌ Error fixing data validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_crisis_data_validation())
