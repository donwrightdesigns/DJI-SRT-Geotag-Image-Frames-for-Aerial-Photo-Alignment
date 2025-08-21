# DJI Frame Geotagging Script

![Geotagged Aerial Video Frames for Photogrammetry](http://www.donwrightdesigns.com/wp-content/uploads/2025/07/Geotag-Image.jpg)

![Shutter Encoder Logo](http://www.donwrightdesigns.com/wp-content/uploads/2025/06/shutter-encoder.jpg)

A Python script that automatically geotags DJI drone image frames using GPS coordinates and altitude data from corresponding .SRT subtitle files.

## Overview

This script solves the problem of geotagging extracted video frames from DJI drones. When DJI drones record videos, they create .SRT subtitle files containing detailed telemetry data including GPS coordinates, altitudes, and other flight information. This script parses that telemetry data and embeds the GPS information directly into the EXIF data of extracted image frames.

**Photogrammetry Compatibility**: This script has been tested and verified for proper GPS import with **Agisoft Metashape** and **Epic Reality Scan Capture**. The embedded EXIF GPS data is recognized and used for automatic georeferencing during photogrammetry processing.

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

- **Photogrammetry Ready**: EXIF GPS data is formatted for compatibility with professional photogrammetry software

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

## Recommended Frame Extraction Workflow

### Using Shutter Encoder + FFmpeg

For optimal compatibility with this geotagging script, we recommend using **Shutter Encoder** to extract frames from your DJI videos. Shutter Encoder uses FFmpeg under the hood and can be configured to output frames with the exact naming convention this script expects.

#### Shutter Encoder Setup:

1. **Download Shutter Encoder**: Get it from [shutterencoder.com](https://www.shutterencoder.com/)

2. **Configure Frame Extraction**:
   - Load your DJI video file (e.g., `DJI_0609.MP4`)
   - Select **"Extract"** function from the dropdown
   - Choose **"All frames"** or set a custom frame rate (e.g., 5 fps)
   - In **Advanced Features**, set the naming pattern to include `_SE_` suffix:
     ```
     Output name format: [filename]_SE_[frame_number]
     ```

3. **Output Settings**:
   - **Format**: JPEG
   - **Frame rate**: 5 fps (recommended for most geotagging purposes)
   - **Output folder**: Same directory as your .SRT files

4. **Start Extraction**: Shutter Encoder will create files like:
   ```
   DJI_0609_SE_000001.jpg
   DJI_0609_SE_000002.jpg
   DJI_0609_SE_000003.jpg
   ...
   ```

#### Why Shutter Encoder?

- **Consistent Naming**: Automatically creates the `_SE_` suffix that this script requires
- **Frame Rate Control**: Easy to set extraction rates (1 fps, 5 fps, etc.)
- **Batch Processing**: Can process multiple videos at once
- **Quality Control**: Maintains high image quality during extraction
- **User-Friendly**: No command-line knowledge required

### Alternative: Direct FFmpeg Commands

If you prefer command-line tools, you can use FFmpeg directly with proper naming:

```bash
# Extract every 6th frame (5 fps from 29.97 fps video) with SE naming
ffmpeg -i DJI_0609.MP4 -vf "fps=5" -f image2 "DJI_0609_SE_%06d.jpg"

# Extract frames at specific intervals
ffmpeg -i DJI_0609.MP4 -vf "select=not(mod(n\\,6))" -vsync vfr -f image2 "DJI_0609_SE_%06d.jpg"
```

**Note**: When using direct FFmpeg commands, ensure the output naming pattern matches `DJI_XXXX_SE_YYYYYY.jpg` format.

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

## Complete Workflow Integration

This script works as a perfect post-processing step after frame extraction. The complete workflow is:

1. **Record**: Fly your DJI drone and record video (creates .MP4 + .SRT files)
2. **Extract**: Use Shutter Encoder to extract frames with `_SE_` naming
3. **Geotag**: Run this script to embed GPS data from .SRT into extracted frames
4. **Use**: Your geotagged frames are ready for GIS, mapping, or analysis software

The key advantage of this workflow is that it maintains perfect timing alignment between your extracted frames and the GPS telemetry data in the SRT files.

## Photogrammetry Software Compatibility

### Tested and Verified:
- **Agisoft Metashape**: GPS coordinates are automatically imported and used for georeferencing
- **Epic Reality Scan Capture**: EXIF GPS data is properly recognized for photogrammetry processing

### Expected Compatibility:
- **Pix4D**: Should work with standard EXIF GPS tags
- **3DF Zephyr**: Should recognize embedded GPS coordinates
- **OpenDroneMap**: Compatible with EXIF GPS metadata
- **DroneDeploy**: Should import GPS data for processing

*Note: While the script follows standard EXIF GPS formatting, compatibility with other photogrammetry software may vary. The GPS data format has been specifically tested and confirmed working with Agisoft Metashape and Epic Reality Scan Capture.*

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

6. **Photogrammetry software not reading GPS**: 
   - Verify EXIF data with ExifTool: `exiftool -gps:all image.jpg`
   - Ensure software is configured to read EXIF GPS data
   - Some software may require specific coordinate reference systems

### Validation

After geotagging, you can verify the embedded GPS data using:
- **ExifTool**: `exiftool -gps:all image.jpg`
- **Photo editing software** that displays GPS information
- **Online EXIF viewers**
- **Agisoft Metashape**: Check the "Import GPS" option during photo loading
- **Epic Reality Scan Capture**: Verify GPS coordinates in the project properties

## License

This script is provided as-is for educational and practical use. Feel free to modify and adapt for your specific needs.

## Contributing

Bug reports, feature requests, and pull requests are welcome. When reporting issues, please include:
- Sample SRT file content (anonymized GPS coordinates if needed)
- Image filename examples
- Error messages or unexpected behavior descriptions
- Photogrammetry software being used (if GPS import issues)

---

**Note**: This script specifically targets DJI drone telemetry format. Other drone manufacturers may use different SRT formats that would require modifications to the parsing logic.
