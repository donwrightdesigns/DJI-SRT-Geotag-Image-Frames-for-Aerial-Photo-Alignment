# DJI Frame Geotagging Script

A Python script that automatically geotags DJI drone image frames using GPS coordinates and altitude data from corresponding .SRT subtitle files.

## Overview

This script solves the problem of geotagging extracted video frames from DJI drones. When DJI drones record videos, they create .SRT subtitle files containing detailed telemetry data including GPS coordinates, altitudes, and other flight information. This script parses that telemetry data and embeds the GPS information directly into the EXIF data of extracted image frames.

## Features

- **DJI SRT Format Support**: Parses the complex DJI .SRT format containing GPS data like:
  ```
  [latitude: 35.999215] [longitude: -86.437040] [rel_alt: 73.800 abs_alt: 204.914]
  ```

- **Flexible Frame Rate Support**: Handles different original video frame rates and frame extraction rates
  - Default: 29.97 fps original video, 5 fps extraction rate
  - Automatically calculates correct timestamp alignment

- **Absolute Altitude**: Uses absolute altitude (above sea level) instead of relative altitude for more accurate geographic referencing

- **Automatic File Matching**: Intelligently matches .SRT files with corresponding image frames based on DJI naming conventions:
  - `DJI_0609.SRT` → `DJI_0609_SE_000001.jpg`, `DJI_0609_SE_000002.jpg`, etc.

- **Batch Processing**: Processes multiple video groups in a single run

- **Detailed Logging**: Provides comprehensive feedback on the geotagging process

## Requirements

### Python Libraries
```bash
pip install piexif pysrt
```

### File Structure
The script expects files in the same directory with this naming convention:
- **SRT files**: `DJI_XXXX.SRT` (e.g., `DJI_0609.SRT`)
- **Image files**: `DJI_XXXX_SE_YYYYYY.jpg` (e.g., `DJI_0609_SE_000001.jpg`)

Where:
- `XXXX` is the video number (must match between SRT and images)
- `YYYYYY` is the sequential frame number

## Usage

1. **Prepare your files**: Place all DJI .SRT files and extracted .jpg frames in the same directory

2. **Run the script**:
   ```bash
   python frame_geotag_dji.py
   ```

3. **Enter frame rates when prompted**:
   - **Original video frame rate**: The FPS of the original drone video (typically 29.97 fps)
   - **Frame extraction rate**: How many frames per second were extracted (e.g., 5 fps = every 6th frame)

4. **Review the output**: The script will show detailed progress for each video group and frame

## Example Output

```
Searching for DJI images and .SRT files in: D:\Drone_Videos\Frames

Found 3 video groups:
  DJI_0609: 35 images, SRT: DJI_0609.SRT
  DJI_0610: 531 images, SRT: DJI_0610.SRT
  DJI_0611: 431 images, SRT: DJI_0611.SRT

--- Video Frame Rate Settings ---
Enter original video frame rate (default: 29.97 fps): 
Enter frame extraction rate (frames extracted per second, default: 5 fps): 
Original video: 29.97 fps
Frame extraction: 5.0 fps (every 6.0 frames)

--- Processing DJI_0609 ---
Successfully parsed DJI_0609.SRT (350 subtitle entries)
  Tagging DJI_0609_SE_000001.jpg (frame 1) with Lat: 35.999215, Lon: -86.437040, Alt: 204.914m, Rel: 73.800m
  Tagging DJI_0609_SE_000002.jpg (frame 2) with Lat: 35.999220, Lon: -86.437035, Alt: 204.920m, Rel: 73.805m
  ...
  Group DJI_0609: Successfully geotagged 35 of 35 images

=== GEOTAGGING COMPLETE ===
Successfully geotagged 997 of 997 images across 3 videos.
Images now contain GPS coordinates with absolute altitude above sea level.
```

## Technical Details

### GPS Data Parsing
The script uses regular expressions to extract GPS data from DJI's complex SRT format:
- **Latitude**: `[latitude: XX.XXXXXX]`
- **Longitude**: `[longitude: -XX.XXXXXX]`
- **Relative Altitude**: `[rel_alt: XX.XXX`
- **Absolute Altitude**: `abs_alt: XXX.XXX]`

### EXIF GPS Tags
The following GPS EXIF tags are embedded in each image:
- `GPSLatitude` / `GPSLatitudeRef`: Decimal degrees converted to degrees/minutes/seconds
- `GPSLongitude` / `GPSLongitudeRef`: Decimal degrees converted to degrees/minutes/seconds  
- `GPSAltitude` / `GPSAltitudeRef`: Absolute altitude in meters above sea level

### Timestamp Calculation
Frame timestamps are calculated using the extraction frame rate:
```python
frame_time_seconds = (frame_number - 1) / extraction_fps
```

This ensures proper alignment between extracted frames and the corresponding GPS data in the SRT file.

## Troubleshooting

### Common Issues

1. **No SRT files found**: Ensure .SRT files start with "DJI_" and have .srt extension

2. **No image files found**: Images must follow the pattern `DJI_XXXX_SE_YYYYYY.jpg`

3. **No matching files**: The prefix before "_SE_" in image names must exactly match the SRT filename (without extension)

4. **Wrong GPS coordinates**: 
   - Check that longitude signs are correct (negative for western hemisphere)
   - Verify frame rate settings match your extraction process

5. **Permission errors**: Ensure write access to image files (remove read-only attributes if necessary)

### Validation

After geotagging, you can verify the embedded GPS data using:
- **ExifTool**: `exiftool -gps:all image.jpg`
- **Photo editing software** that displays GPS information
- **Online EXIF viewers**

## Integration with Video Processing Workflows

This script works well as a post-processing step after extracting frames with tools like:
- **FFmpeg**: `ffmpeg -i video.mp4 -vf fps=5 frame_%06d.jpg`
- **Shutter Encoder**: Using the "Extract" function
- **Other video editing software**

The key is ensuring the extracted frames maintain the sequential numbering that corresponds to the timing in the original video.

## License

This script is provided as-is for educational and practical use. Feel free to modify and adapt for your specific needs.

## Contributing

Bug reports, feature requests, and pull requests are welcome. When reporting issues, please include:
- Sample SRT file content (anonymized GPS coordinates if needed)
- Image filename examples
- Error messages or unexpected behavior descriptions

---

**Note**: This script specifically targets DJI drone telemetry format. Other drone manufacturers may use different SRT formats that would require modifications to the parsing logic.
