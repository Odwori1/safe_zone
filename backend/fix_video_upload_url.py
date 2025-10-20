# Read the uploads.py file
with open('app/api/endpoints/uploads.py', 'r') as f:
    content = f.read()

# Find the exact line in the video upload URL function that needs fixing
# We need to add content_type='video' to the generate_upload_url call

# The problematic line is around line 100-104
old_line = '        upload_data = await file_upload_handler.generate_upload_url('
new_line = '        upload_data = await file_upload_handler.generate_upload_url('

# Find and replace the specific generate_upload_url call in the video endpoint
import re

# Pattern to find the video upload URL generation call
pattern = r'(upload_data = await file_upload_handler\.generate_upload_url\s*\()([^)]+)(\))'

def replace_video_upload(match):
    opening = match.group(1)
    params = match.group(2)
    closing = match.group(3)
    
    # Add content_type='video' to the parameters
    if 'content_type=' not in params:
        # Add it as the first parameter
        new_params = "content_type='video', " + params
    else:
        # Replace existing content_type
        new_params = re.sub(r"content_type=['\"][^'\"]*['\"]", "content_type='video'", params)
    
    return opening + new_params + closing

# Apply the replacement
new_content = re.sub(pattern, replace_video_upload, content)

# Write the fixed content
with open('app/api/endpoints/uploads.py', 'w') as f:
    f.write(new_content)

print("✅ Fixed video upload URL generation - added content_type='video' parameter")
