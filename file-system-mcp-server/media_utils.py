import os
import platform
import json
from datetime import datetime

# Import platform-specific utilities
if platform.system() == "Windows":
    try:
        from windows_utils import (
            get_windows_drives,
            get_windows_special_folders,
            get_windows_environment,
            get_windows_system_info,
            normalize_windows_path,
            is_valid_windows_path
        )
    except ImportError:
        print("Windows utilities could not be imported. Some features may be limited.")

# Image processing utilities
def get_image_metadata(file_path):
    """
    Get detailed metadata for an image file.
    Requires Pillow library.
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        if not os.path.isfile(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Basic file metadata
        stat_info = os.stat(file_path)
        metadata = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": stat_info.st_size,
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "type": "image"
        }
        
        # Get image-specific metadata
        try:
            with Image.open(file_path) as img:
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                metadata["width"] = img.width
                metadata["height"] = img.height
                
                # Get EXIF data if available
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    for tag_id, value in img._getexif().items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
                
                if exif_data:
                    metadata["exif"] = exif_data
        except Exception as e:
            metadata["image_error"] = str(e)
        
        return metadata
    except ImportError:
        return {
            "error": "Pillow library not installed. Install with: pip install Pillow",
            "basic_info": {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}

# Video processing utilities
def get_video_metadata(file_path):
    """
    Get detailed metadata for a video file.
    Requires ffmpeg-python library.
    """
    try:
        import ffmpeg
        
        if not os.path.isfile(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Basic file metadata
        stat_info = os.stat(file_path)
        metadata = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": stat_info.st_size,
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "type": "video"
        }
        
        # Get video-specific metadata
        try:
            probe = ffmpeg.probe(file_path)
            
            # Get video stream info
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream:
                metadata["video"] = {
                    "codec": video_stream.get('codec_name'),
                    "width": int(video_stream.get('width', 0)),
                    "height": int(video_stream.get('height', 0)),
                    "duration": float(video_stream.get('duration', 0)),
                    "bit_rate": int(video_stream.get('bit_rate', 0)) if 'bit_rate' in video_stream else None,
                    "fps": eval(video_stream.get('r_frame_rate', '0/1')) if 'r_frame_rate' in video_stream else None
                }
            
            # Get audio stream info
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            if audio_stream:
                metadata["audio"] = {
                    "codec": audio_stream.get('codec_name'),
                    "channels": int(audio_stream.get('channels', 0)),
                    "sample_rate": int(audio_stream.get('sample_rate', 0)),
                    "bit_rate": int(audio_stream.get('bit_rate', 0)) if 'bit_rate' in audio_stream else None
                }
            
            # Get format info
            if 'format' in probe:
                metadata["format"] = {
                    "name": probe['format'].get('format_name'),
                    "duration": float(probe['format'].get('duration', 0)),
                    "bit_rate": int(probe['format'].get('bit_rate', 0)) if 'bit_rate' in probe['format'] else None
                }
        except Exception as e:
            metadata["video_error"] = str(e)
        
        return metadata
    except ImportError:
        return {
            "error": "ffmpeg-python library not installed. Install with: pip install ffmpeg-python",
            "basic_info": {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}

# Audio processing utilities
def get_audio_metadata(file_path):
    """
    Get detailed metadata for an audio file.
    Requires mutagen library.
    """
    try:
        import mutagen
        
        if not os.path.isfile(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Basic file metadata
        stat_info = os.stat(file_path)
        metadata = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": stat_info.st_size,
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "type": "audio"
        }
        
        # Get audio-specific metadata
        try:
            audio = mutagen.File(file_path)
            if audio:
                # Extract common metadata
                metadata["audio"] = {
                    "length": audio.info.length,
                    "bitrate": audio.info.bitrate
                }
                
                # Extract tags
                tags = {}
                if hasattr(audio, 'tags') and audio.tags:
                    for key in audio.tags.keys():
                        tags[key] = str(audio.tags[key])
                
                if tags:
                    metadata["tags"] = tags
        except Exception as e:
            metadata["audio_error"] = str(e)
        
        return metadata
    except ImportError:
        return {
            "error": "mutagen library not installed. Install with: pip install mutagen",
            "basic_info": {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}

# Thumbnail generation
def generate_thumbnail(file_path, output_path=None, size=(128, 128)):
    """
    Generate a thumbnail for an image or video file.
    Requires Pillow for images and ffmpeg-python for videos.
    """
    file_type = os.path.splitext(file_path)[1].lower()
    
    # Default output path if not specified
    if not output_path:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(os.path.dirname(file_path), f"{base_name}_thumb.jpg")
    
    # Image thumbnails
    if file_type in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                img.thumbnail(size)
                img.save(output_path, "JPEG")
            
            return {
                "success": True,
                "thumbnail_path": output_path,
                "original_path": file_path
            }
        except ImportError:
            return {"error": "Pillow library not installed. Install with: pip install Pillow"}
        except Exception as e:
            return {"error": str(e)}
    
    # Video thumbnails
    elif file_type in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']:
        try:
            import ffmpeg
            
            # Extract a frame at 1 second or 10% of the video, whichever is smaller
            try:
                probe = ffmpeg.probe(file_path)
                duration = float(probe['format']['duration'])
                time = min(1, duration * 0.1)
                
                (
                    ffmpeg
                    .input(file_path, ss=time)
                    .filter('scale', size[0], size[1])
                    .output(output_path, vframes=1)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                
                return {
                    "success": True,
                    "thumbnail_path": output_path,
                    "original_path": file_path,
                    "frame_time": time
                }
            except Exception as e:
                return {"error": f"Failed to generate video thumbnail: {str(e)}"}
        except ImportError:
            return {"error": "ffmpeg-python library not installed. Install with: pip install ffmpeg-python"}
        except Exception as e:
            return {"error": str(e)}
    
    else:
        return {"error": f"Unsupported file type for thumbnail generation: {file_type}"}

# File organization utilities
def organize_by_date(files, output_dir=None):
    """
    Organize files by creation date.
    Returns a dictionary of files grouped by date.
    """
    if not files:
        return {"error": "No files provided"}
    
    organized = {}
    
    for file_info in files:
        if "created" in file_info:
            try:
                date_str = file_info["created"].split("T")[0]  # Get YYYY-MM-DD part
                
                if date_str not in organized:
                    organized[date_str] = []
                
                organized[date_str].append(file_info)
                
                # Create directories if output_dir is specified
                if output_dir:
                    date_dir = os.path.join(output_dir, date_str)
                    os.makedirs(date_dir, exist_ok=True)
            except Exception as e:
                if "errors" not in organized:
                    organized["errors"] = []
                organized["errors"].append({
                    "file": file_info.get("path", "Unknown"),
                    "error": str(e)
                })
    
    return organized

# File type detection with better accuracy
def detect_file_type(file_path):
    """
    Detect file type with better accuracy using file signatures.
    """
    # File signatures (magic numbers) for common file types
    signatures = {
        # Images
        b'\xFF\xD8\xFF': 'image/jpeg',
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',
        b'\x47\x49\x46\x38': 'image/gif',
        b'\x42\x4D': 'image/bmp',
        b'\x49\x49\x2A\x00': 'image/tiff',
        b'\x4D\x4D\x00\x2A': 'image/tiff',
        
        # Videos
        b'\x00\x00\x00\x18\x66\x74\x79\x70': 'video/mp4',
        b'\x00\x00\x00\x1C\x66\x74\x79\x70': 'video/mp4',
        b'\x00\x00\x00\x20\x66\x74\x79\x70': 'video/mp4',
        b'\x52\x49\x46\x46': 'video/avi',
        b'\x00\x00\x01\xBA': 'video/mpeg',
        b'\x00\x00\x01\xB3': 'video/mpeg',
        
        # Audio
        b'\x49\x44\x33': 'audio/mp3',
        b'\xFF\xFB': 'audio/mp3',
        b'\xFF\xF3': 'audio/mp3',
        b'\xFF\xF2': 'audio/mp3',
        b'\x52\x49\x46\x46': 'audio/wav',
        b'\x4F\x67\x67\x53': 'audio/ogg',
        b'\x66\x4C\x61\x43': 'audio/flac'
    }
    
    try:
        with open(file_path, 'rb') as f:
            # Read first 16 bytes for signature matching
            header = f.read(16)
            
            for signature, mime_type in signatures.items():
                if header.startswith(signature):
                    # Map MIME type to simplified type
                    if mime_type.startswith('image/'):
                        return 'image'
                    elif mime_type.startswith('video/'):
                        return 'video'
                    elif mime_type.startswith('audio/'):
                        return 'audio'
    except Exception:
        pass
    
    # Fallback to extension-based detection
    ext = os.path.splitext(file_path)[1].lower()
    
    # Common image extensions
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        return 'image'
    # Common video extensions
    elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']:
        return 'video'
    # Common audio extensions
    elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']:
        return 'audio'
    
    return 'unknown'
