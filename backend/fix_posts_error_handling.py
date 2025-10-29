import re

# Read the current file
with open('/home/odwori/safe_zone/backend/app/api/endpoints/posts.py', 'r') as f:
    content = f.read()

# Find and replace the generic error handling in like_post
old_like_error = '''    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error liking post: {str(e)}"
        )'''

new_like_error = '''    except Exception as e:
        # Include the full error details for debugging
        error_detail = f"Error liking post: {str(e)}"
        print(f"❌ LIKE ERROR: {error_detail}")  # Log to backend console
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )'''

# Replace in content
content = content.replace(old_like_error, new_like_error)

# Do the same for unlike_post
old_unlike_error = '''    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unliking post: {str(e)}"
        )'''

new_unlike_error = '''    except Exception as e:
        # Include the full error details for debugging
        error_detail = f"Error unliking post: {str(e)}"
        print(f"❌ UNLIKE ERROR: {error_detail}")  # Log to backend console
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )'''

content = content.replace(old_unlike_error, new_unlike_error)

# Write back
with open('/home/odwori/safe_zone/backend/app/api/endpoints/posts.py', 'w') as f:
    f.write(content)

print("✅ Updated error handling in posts endpoints")
