# Read the entire file
with open('app/api/endpoints/posts.py', 'r') as f:
    lines = f.readlines()

# Find the start and end of the video endpoint (lines 291-308)
video_start = 290  # 0-indexed (line 291 is index 290)
video_end = 307    # 0-indexed (line 308 is index 307)

# Find the position after audio endpoint (after line 75)
insert_after = 75  # 0-indexed (line 76 is after audio endpoint)

# Extract the video endpoint block
video_block = lines[video_start:video_end+1]

# Remove the video block from its current position
lines_after_removal = lines[:video_start] + lines[video_end+1:]

# Insert the video block after the audio endpoint
new_lines = lines_after_removal[:insert_after+1] + video_block + ['\n'] + lines_after_removal[insert_after+1:]

# Write the fixed file
with open('app/api/endpoints/posts.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Successfully moved /video endpoint before /{post_id} route")
print("New route order:")
print("1. /")
print("2. /audio") 
print("3. /video  ← MOVED HERE")
print("4. /{post_id}")
print("5. Other routes...")
