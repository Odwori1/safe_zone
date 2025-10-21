# Read the main.py file
with open('app/main.py', 'r') as f:
    content = f.read()

# Add import for new files router
import_statement = 'from app.api.endpoints import health, auth, profiles, posts, comments, journals, mood, crisis, uploads'
new_import = 'from app.api.endpoints import health, auth, profiles, posts, comments, journals, mood, crisis, uploads, files'

content = content.replace(import_statement, new_import)

# Add the new files router
router_statement = 'app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])'
new_router = 'app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])\napp.include_router(files.router, prefix="/api/v1/files", tags=["files"])'

content = content.replace(router_statement, new_router)

# Write updated main.py
with open('app/main.py', 'w') as f:
    f.write(content)

print("✅ Registered new secure files router")
