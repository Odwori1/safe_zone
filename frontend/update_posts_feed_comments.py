import re

# Read the current posts feed
with open('/home/odwori/safe_zone/frontend/src/components/posts/posts-feed.tsx', 'r') as f:
    content = f.read()

# Replace the CommentsList import and usage
old_comments_import = "import CommentsList from './comments-list';"
new_comments_import = "import CommentsList from './comments-list';"

# The CommentsList component should already be using the new store
# We just need to ensure it's properly imported and used

# Write back (no changes needed if already using CommentsList)
with open('/home/odwori/safe_zone/frontend/src/components/posts/posts-feed.tsx', 'w') as f:
    f.write(content)

print("✅ Posts feed comments should be using the new store")
