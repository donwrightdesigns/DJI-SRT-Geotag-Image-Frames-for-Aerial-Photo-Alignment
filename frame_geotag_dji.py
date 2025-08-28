# DJI Frame Geotagging Script
# This script geotags DJI drone image frames using corresponding .SRT subtitle files.
# It requires the 'piexif' and 'pysrt' libraries.
# To install them, run: pip install piexif pysrt

import os
import re
import pysrt
import piexif
from datetime import timedelta
from collections import defaultdict

# --- Helper functions for converting GPS data to EXIF format ---
def to_deg(value, loc):
    """Converts decimal coordinates to degrees, minutes, seconds."""
    if value < 0:
        loc_value = loc[1]
    elif value > 0:
        loc_value = loc[0]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return (deg, min, sec, loc_value)

def parse_dji_gps_data(srt_text):
    """Parse DJI SRT format to extract GPS coordinates and altitude."""
    try:
        # Extract latitude
        lat_match = re.search(r'\[latitude:\s*([-\d.]+)\]', srt_text)
        # Extract longitude  
        lon_match = re.search(r'\[longitude:\s*([-\d.]+)\]', srt_text)
        # Extract both relative and absolute altitude
        rel_alt_match = re.search(r'\[rel_alt:\s*([-\d.]+)', srt_text)
        abs_alt_match = re.search(r'abs_alt:\s*([-\d.]+)\]', srt_text)
        
        if lat_match and lon_match and abs_alt_match:
            lat = float(lat_match.group(1))
            lon = float(lon_match.group(1))
            abs_alt = float(abs_alt_match.group(1))
            rel_alt = float(rel_alt_match.group(1)) if rel_alt_match else None
            
            return lat, lon, abs_alt, rel_alt
        else:
            return None
            
    except (ValueError, AttributeError):
        return None

def set_gps_location(file_path, lat, lon, abs_alt, rel_alt=None):
    """Writes GPS data to an image file's EXIF tags using absolute altitude."""
    try:
        lat_deg = to_deg(lat, ["N", "S"])
        lon_deg = to_deg(lon, ["E", "W"])

        exif_dict = piexif.load(file_path)
        
        # Convert absolute altitude to EXIF format (rational number)
        abs_alt_rational = (int(abs_alt * 100), 100)

        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: lat_deg[3].encode('utf-8'),
            piexif.GPSIFD.GPSLatitude: ((lat_deg[0], 1), (lat_deg[1], 1), (int(lat_deg[2] * 100000), 100000)),
            piexif.GPSIFD.GPSLongitudeRef: lon_deg[3].encode('utf-8'),
            piexif.GPSIFD.GPSLongitude: ((lon_deg[0], 1), (lon_deg[1], 1), (int(lon_deg[2] * 100000), 100000)),
            piexif.GPSIFD.GPSAltitudeRef: 0,  # 0 = Above sea level
            piexif.GPSIFD.GPSAltitude: abs_alt_rational,  # Using absolute altitude
        }
        
        exif_dict["GPS"] = gps_ifd
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)
        return True
        
    except Exception as e:
        print(f"  -> Error writing EXIF data to {file_path}: {e}")
        return False

def extract_video_prefix(filename):
    """Extract DJI video prefix from filename (e.g., 'DJI_0609_SE_000001.jpg' or 'DJI_0609_000001.jpg' -> 'DJI_0609')"""
    # Try pattern with _SE_ first (original format)
    match = re.match(r'(DJI_\d+)_SE_\d+\.jpg$', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Try pattern without _SE_ (alternative format)
    match = re.match(r'(DJI_\d+)_\d+\.jpg$', filename, re.IGNORECASE)
    return match.group(1) if match else None

def extract_frame_number(filename):
    """Extract frame number from filename (e.g., 'DJI_0609_SE_000001.jpg' or 'DJI_0609_000001.jpg' -> 1)"""
    # Try pattern with _SE_ first (original format)
    match = re.search(r'_SE_(\d+)\.jpg$', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Try pattern without _SE_ (alternative format)
    match = re.search(r'_([^_]+)\.jpg$', filename, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None

def geotag_dji_frames():
    """Finds DJI images and SRT files in the current directory and geotags them."""
    
    current_folder = os.getcwd()
    print(f"Searching for DJI images and .SRT files in: {current_folder}")

    # 1. Find SRT files and group images by video prefix
    srt_files = {}
    image_groups = defaultdict(list)
    
    for f in sorted(os.listdir(current_folder)):
        if f.lower().endswith(".srt") and f.startswith("DJI_"):
            # Extract prefix from SRT file (e.g., DJI_0609.SRT -> DJI_0609)
            prefix = f[:-4]  # Remove .SRT extension
            srt_files[prefix] = f
            
        elif f.lower().endswith(".jpg") and f.startswith("DJI_"):
            # Group images by their video prefix (both _SE_ and non-_SE_ formats)
            prefix = extract_video_prefix(f)
            if prefix:
                frame_num = extract_frame_number(f)
                if frame_num is not None:
                    image_groups[prefix].append((f, frame_num))

    if not srt_files:
        print("Error: No DJI .SRT files found in this folder. Exiting.")
        return
        
    if not image_groups:
        print("Error: No DJI image files found (formats: DJI_XXXX_SE_XXXXXX.jpg or DJI_XXXX_XXXXXX.jpg). Exiting.")
        return

    # Match SRT files with image groups
    matched_groups = {}
    for prefix in srt_files:
        if prefix in image_groups:
            matched_groups[prefix] = {
                'srt_file': srt_files[prefix],
                'images': sorted(image_groups[prefix], key=lambda x: x[1])  # Sort by frame number
            }

    if not matched_groups:
        print("Error: No matching SRT files found for image prefixes.")
        print(f"SRT prefixes found: {list(srt_files.keys())}")
        print(f"Image prefixes found: {list(image_groups.keys())}")
        return

    print(f"\nFound {len(matched_groups)} video groups:")
    for prefix, data in matched_groups.items():
        print(f"  {prefix}: {len(data['images'])} images, SRT: {data['srt_file']}")

    # 2. Get video properties from user
    print("\n--- Video Frame Rate Settings ---")
    
    # Get original video FPS
    video_fps_input = input("Enter original video frame rate (default: 29.97 fps): ").strip()
    if video_fps_input:
        try:
            video_fps = float(video_fps_input)
        except ValueError:
            print("Invalid frame rate. Using default 29.97 fps.")
            video_fps = 29.97
    else:
        video_fps = 29.97
    
    # Get frame extraction rate
    extraction_fps_input = input("Enter frame extraction rate (frames extracted per second, default: 5 fps): ").strip()
    if extraction_fps_input:
        try:
            extraction_fps = float(extraction_fps_input)
        except ValueError:
            print("Invalid extraction rate. Using default 5 fps.")
            extraction_fps = 5.0
    else:
        extraction_fps = 5.0
        
    print(f"Original video: {video_fps} fps")
    print(f"Frame extraction: {extraction_fps} fps (every {video_fps/extraction_fps:.1f} frames)")

    # 3. Process each video group
    total_success = 0
    total_images = 0
    
    for prefix, data in matched_groups.items():
        print(f"\n--- Processing {prefix} ---")
        srt_file = data['srt_file']
        images = data['images']
        
        # Parse the SRT file
        try:
            subs = pysrt.open(srt_file)
            print(f"Successfully parsed {srt_file} ({len(subs)} subtitle entries)")
        except Exception as e:
            print(f"Error parsing {srt_file}: {e}")
            continue

        # Process each image in this group
        group_success = 0
        for img_filename, frame_number in images:
            total_images += 1
            
            # Calculate the timestamp of the current frame using extraction rate
            # Frame numbering is 1-based, so subtract 1 for 0-based calculation
            frame_time_seconds = (frame_number - 1) / extraction_fps
            frame_timedelta_ms = frame_time_seconds * 1000  # Convert to milliseconds for SRT comparison
            
            # Find the subtitle entry that contains this frame's timestamp
            gps_data_found = False
            for sub in subs:
                # Convert SRT timedelta to milliseconds
                sub_start_ms = sub.start.ordinal
                sub_end_ms = sub.end.ordinal
                
                if sub_start_ms <= frame_timedelta_ms <= sub_end_ms:
                    # Parse DJI GPS data from this subtitle
                    gps_result = parse_dji_gps_data(sub.text)
                    if gps_result:
                        lat, lon, abs_alt, rel_alt = gps_result
                        
                        full_image_path = os.path.join(current_folder, img_filename)
                        rel_alt_str = f", Rel: {rel_alt}m" if rel_alt is not None else ""
                        print(f"  Tagging {img_filename} (frame {frame_number}) with Lat: {lat}, Lon: {lon}, Alt: {abs_alt}m{rel_alt_str}")
                        
                        if set_gps_location(full_image_path, lat, lon, abs_alt, rel_alt):
                            group_success += 1
                            total_success += 1
                        gps_data_found = True
                        break
                    else:
                        print(f"  -> Warning: Could not parse GPS data from SRT entry: '{sub.text[:50]}...'")
                        break
            
            if not gps_data_found:
                print(f"  -> Warning: No matching GPS data found for {img_filename} (frame {frame_number}, time: {frame_time_seconds:.3f}s)")
        
        print(f"  Group {prefix}: Successfully geotagged {group_success} of {len(images)} images")

    print("\n=== GEOTAGGING COMPLETE ===")
    print(f"Successfully geotagged {total_success} of {total_images} images across {len(matched_groups)} videos.")
    print("Images now contain GPS coordinates with absolute altitude above sea level.")

# --- Run the main function ---
if __name__ == "__main__":
    geotag_dji_frames()
