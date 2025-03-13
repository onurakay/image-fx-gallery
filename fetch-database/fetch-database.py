import sys
import os
import json
import glob
from datetime import datetime
from PIL import Image
from fractions import Fraction  # Needed for aspect ratio calculation

# Force UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Ratio calculation mechanism
STANDARD_RATIOS = {
    (1, 1): "1:1",
    (9, 16): "9:16",
    (16, 9): "16:9",
    (3, 4): "3:4",
    (4, 3): "4:3",
    (2, 3): "2:3",
    (3, 2): "3:2"
}

def get_standard_aspect_ratio(width, height):
    """Returns the closest standard aspect ratio for the given dimensions."""
    fraction = Fraction(width, height).limit_denominator(16)  # Limit denominator to avoid odd fractions
    ratio_tuple = (fraction.numerator, fraction.denominator)
    return STANDARD_RATIOS.get(ratio_tuple, f"{fraction.numerator}:{fraction.denominator}")

# Get the path of the current script (app.py)
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))  # e.g. 'fetch-database/imagefx/'

# Correctly point to json and jpg folders inside 'imagefx/'
JSON_FOLDER = os.path.join(BASE_FOLDER, "imagefx", "json")  # JSON folder inside imagefx
IMAGE_FOLDER = os.path.join(BASE_FOLDER, "imagefx", "jpg")  # JPG folder inside imagefx

# Output file path (inside 'imagefx/')
OUTPUT_COMBINED = os.path.join(BASE_FOLDER, "combined.json")

def extract_creation_time(imageid):
    """Extracts and formats the creation time from the imageid."""
    try:
        time_part = imageid[:14]  # Example: '15265408022025'
        hour = time_part[0:2]
        minute = time_part[2:4]
        second = time_part[4:6]
        day = time_part[6:8]
        month = time_part[8:10]
        year = time_part[10:14]
        created_at = f"{year}-{month}-{day} {hour}:{minute}:{second}"
        return created_at
    except Exception as e:
        print(f"Error extracting creation time from imageid '{imageid}': {e}")
        return None

def combine_json_files(json_folder, image_folder, output_filename):
    """
    Combines JSON files and expands images into separate entries.
    For each image found, it creates a thumbnail (if missing) and calculates the aspect ratio,
    which is then added to the output JSON.
    """
    if not os.path.exists(json_folder):
        print(f"Error: The JSON folder '{json_folder}' does not exist!")
        return None

    combined_data = []
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

    if not json_files:
        print("Warning: No JSON files found in the folder.")
        return None

    for filename in json_files:
        filepath = os.path.join(json_folder, filename)
        print(f"Processing JSON file: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Ensure data is a list
                if isinstance(data, dict):
                    data = [data]

                for entry in data:
                    if "imageid" in entry:
                        imageid = entry["imageid"]
                        created_at = extract_creation_time(imageid)

                        # Find image files for this imageid
                        pattern = os.path.join(image_folder, f"imagefx_{imageid}_*")
                        matching_paths = glob.glob(pattern)
                        matching_files = []

                        if not matching_paths:
                            print(f"Warning: No images found for imageid '{imageid}'")
                            continue

                        for image_path in matching_paths:
                            image_filename = os.path.basename(image_path)
                            thumbnail_filename = f"timg_{image_filename}"
                            thumbnail_path = os.path.join(image_folder, thumbnail_filename)

                            # Process the image to calculate aspect ratio and create thumbnail if needed
                            try:
                                with Image.open(image_path) as img:
                                    width, height = img.size
                                    aspect_ratio = get_standard_aspect_ratio(width, height)
                                    
                                    # Create thumbnail if it doesn't exist
                                    if not os.path.exists(thumbnail_path):
                                        # Calculate 25% of the size while maintaining aspect ratio
                                        new_width = int(width * 0.25)
                                        new_height = int(height * 0.25)
                                        img_copy = img.copy()  # Avoid modifying the original image
                                        img_copy.thumbnail((new_width, new_height))
                                        img_copy.save(thumbnail_path)
                                        print(f"Created thumbnail: {thumbnail_filename}")
                                    else:
                                        print(f"Thumbnail exists: {thumbnail_filename}")
                            except Exception as e:
                                print(f"Error processing image {image_filename}: {e}")
                                continue

                            # Append the image details including aspect ratio
                            matching_files.append({
                                "image_file": image_filename,
                                "aspect_ratio": aspect_ratio
                            })

                        # Create a separate entry for each image file found
                        for item in matching_files:
                            new_entry = {
                                "prompt": entry.get("prompt", ""),
                                "imageid": imageid,
                                "created_at": created_at,
                                "seed": entry.get("seed", ""),
                                "image_file": item["image_file"],
                                "aspect_ratio": item["aspect_ratio"]
                            }
                            combined_data.append(new_entry)

        except json.JSONDecodeError as e:
            print(f"Error reading {filename}: {e}")

    if not combined_data:
        print("No valid data found. The output JSON will be empty.")

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        json.dump(combined_data, outfile, indent=2, ensure_ascii=False)

    print(f"Combined JSON saved to {output_filename}")
    return output_filename

def main():
    if not os.path.exists(JSON_FOLDER):
        print(f"Error: The folder '{JSON_FOLDER}' does not exist. Please check your folder structure.")
        return

    if not os.path.exists(IMAGE_FOLDER):
        print(f"Error: The folder '{IMAGE_FOLDER}' does not exist. Please check your folder structure.")
        return

    combine_json_files(JSON_FOLDER, IMAGE_FOLDER, OUTPUT_COMBINED)

if __name__ == "__main__":
    main()
