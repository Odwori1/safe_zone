# Script to remove the duplicate FileUploadResponse class
import re

# Read the current file
with open('app/schemas/post.py', 'r') as f:
    content = f.read()

# Find and remove the duplicate class (the one that inherits from TimeStampedSchema)
# We'll keep the correct one that has upload_url, file_id, s3_key, expires_in

# Split the content to find the problematic section
lines = content.split('\n')

# Find the start and end of the duplicate class
start_line = None
end_line = None
in_class = False
class_indent = 0

for i, line in enumerate(lines):
    if 'class FileUploadResponse(TimeStampedSchema):' in line:
        start_line = i
        in_class = True
        class_indent = len(line) - len(line.lstrip())
        continue
    
    if in_class:
        # Check if we've reached the next class or the end of the class
        current_indent = len(line) - len(line.lstrip()) if line.strip() else 0
        if (line.strip().startswith('class ') and current_indent == class_indent) or \
           (i > start_line and current_indent <= class_indent and line.strip() and not line.startswith(' ' * (class_indent + 4))):
            end_line = i
            break

# If we found the duplicate class, remove it
if start_line is not None and end_line is not None:
    # Remove the duplicate class
    new_lines = lines[:start_line] + lines[end_line:]
    new_content = '\n'.join(new_lines)
    
    # Write the fixed content
    with open('app/schemas/post.py', 'w') as f:
        f.write(new_content)
    
    print("✅ SUCCESS: Removed duplicate FileUploadResponse class")
    print(f"✅ Removed lines {start_line + 1} to {end_line + 1}")
else:
    print("❌ Could not find the duplicate class to remove")

