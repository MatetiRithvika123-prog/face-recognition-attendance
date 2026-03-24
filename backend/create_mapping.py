import os
import json
import shutil
from datetime import datetime

# Paths
extracted_dir = r"C:\Users\Mateti\OneDrive\Desktop\rtp\backend\dataset\extracted_images"
trainer_dir = r"C:\Users\Mateti\OneDrive\Desktop\rtp\backend\trainer"
output_file = os.path.join(trainer_dir, "student_mapping.json")

# Create trainer directory if it doesn't exist
os.makedirs(trainer_dir, exist_ok=True)

# Load existing student info if available
student_info = {}
if os.path.exists(os.path.join(trainer_dir, "student_info.json")):
    with open(os.path.join(trainer_dir, "student_info.json"), 'r') as f:
        student_info = json.load(f)

# Create a backup of the original file
if os.path.exists(output_file):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(trainer_dir, f"student_mapping_backup_{timestamp}.json")
    shutil.copy2(output_file, backup_file)
    print(f"Created backup at: {backup_file}")

# Get all face images
face_images = [f for f in os.listdir(extracted_dir) if f.endswith('.jpg') and 'face' in f]

# Create mapping template
mapping = {}
for i, img in enumerate(sorted(face_images), 1):
    mapping[img] = {
        "roll": f"R{1000 + i}",
        "name": f"Student {i}",
        "branch": "CSE",  # Update this as needed
        "actual_name": "",  # Fill this in
        "actual_roll": ""   # Fill this in
    }

# Save the mapping file
with open(output_file, 'w') as f:
    json.dump(mapping, f, indent=2)

print(f"Mapping template created at: {output_file}")
print("Please edit this file to add actual student information.")
