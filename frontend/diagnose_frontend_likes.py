import os

def read_file_sections(filepath, search_terms):
    """Read specific sections of a file"""
    if not os.path.exists(filepath):
        return f"❌ File not found: {filepath}"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    results = []
    for term in search_terms:
        if term in content:
            # Find the section around the search term
            idx = content.find(term)
            start = max(0, idx - 200)
            end = min(len(content), idx + 500)
            section = content[start:end]
            results.append(f"🔍 Found '{term}':\n{section}\n{'-'*80}\n")
        else:
            results.append(f"❌ '{term}' not found in {filepath}\n")
    
    return '\n'.join(results)

print("🔍 FRONTEND LIKES SYSTEM DIAGNOSIS")
print("=" * 60)

# Check posts store
print("\n1. POSTS STORE (posts-store.ts):")
posts_store_path = os.path.expanduser("~/safe_zone/frontend/src/stores/posts-store.ts")
print(read_file_sections(posts_store_path, ["likePost", "unlikePost"]))

# Check posts feed
print("\n2. POSTS FEED (posts-feed.tsx):")
posts_feed_path = os.path.expanduser("~/safe_zone/frontend/src/components/posts/posts-feed.tsx")
print(read_file_sections(posts_feed_path, ["handleLikePost", "onLike", "likePost"]))

# Check post actions
print("\n3. POST ACTIONS (post-actions.tsx):")
post_actions_path = os.path.expanduser("~/safe_zone/frontend/src/components/posts/post-actions.tsx")
print(read_file_sections(post_actions_path, ["handleLike", "onLike", "isLiked"]))

# Check API client
print("\n4. API CLIENT (api-client.ts):")
api_client_path = os.path.expanduser("~/safe_zone/frontend/src/lib/api-client.ts")
print(read_file_sections(api_client_path, ["request", "500", "error"]))

# Check post types
print("\n5. POST TYPES (posts.ts):")
posts_types_path = os.path.expanduser("~/safe_zone/frontend/src/types/posts.ts")
print(read_file_sections(posts_types_path, ["like", "PostResponse", "user_has_liked"]))
