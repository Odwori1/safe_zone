# Read the feed.py file
with open('app/crud/feed.py', 'r') as f:
    content = f.read()

# Fix the parameter numbering in get_post_feed function
old_code = '''    query += " ORDER BY p.created_at DESC LIMIT $2 OFFSET $3"
    params.extend([limit, skip])

    # Use the correct database method
    rows = await database.fetch(query, *params)'''

new_code = '''    # Fix parameter numbering - LIMIT and OFFSET come after all filters
    query += f" ORDER BY p.created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
    params.extend([limit, skip])

    # Use the correct database method
    rows = await database.fetch(query, *params)'''

# Replace the problematic section
content = content.replace(old_code, new_code)

# Write the fixed content
with open('app/crud/feed.py', 'w') as f:
    f.write(content)

print("✅ Fixed feed parameter numbering")
