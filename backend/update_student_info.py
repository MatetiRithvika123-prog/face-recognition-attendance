import os
import json
import shutil
from datetime import datetime

# Paths
trainer_dir = r"C:\Users\Mateti\OneDrive\Desktop\rtp\backend\trainer"
mapping_file = os.path.join(trainer_dir, "student_mapping.json")
output_file = os.path.join(trainer_dir, "student_info.json")

# Check if mapping file exists
if not os.path.exists(mapping_file):
    print(f"Error: Mapping file not found at {mapping_file}")
    print("Please run create_mapping.py first.")
    exit(1)

# Create backup of existing student info
if os.path.exists(output_file):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(trainer_dir, f"student_info_backup_{timestamp}.json")
    shutil.copy2(output_file, backup_file)
    print(f"Created backup at: {backup_file}")

# Load the mapping
with open(mapping_file, 'r') as f:
    mapping = json.load(f)

# Create updated student info
updated_info = {}
for i, (img_name, info) in enumerate(mapping.items(), 1):
    # Use actual information if available, otherwise use defaults
    roll = info.get("actual_roll") or info["roll"]
    name = info.get("actual_name") or info["name"]
    
    updated_info[str(i)] = {
        "roll": roll,
        "name": name,
        "branch": info["branch"],
        "image": img_name  # Store the original image filename for reference
    }

# Save the updated info
with open(output_file, 'w') as f:
    json.dump(updated_info, f, indent=2)

print(f"Updated student information saved to {output_file}")
print(f"Processed {len(updated_info)} student records.")

# Verify the output
print("\nSample of updated student information:")
for i, (k, v) in enumerate(list(updated_info.items())[:3], 1):
    print(f"{i}. {v['name']} (Roll: {v['roll']}, Branch: {v['branch']})")

if len(updated_info) > 3:
    print(f"... and {len(updated_info) - 3} more")
