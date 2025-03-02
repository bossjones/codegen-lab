#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to detect objects or tweet content in images and draw bounding boxes.

This script uses Google's Generative AI (Gemini) to analyze images and:
1. Detect tweet components (profile picture, username, content) and draw a bounding box
2. Detect general objects in images and draw labeled bounding boxes for each

The script supports command-line arguments for customizing detection mode, input/output paths,
and appearance of the bounding boxes.
"""
import google.generativeai as genai
import PIL.Image
import PIL.ImageDraw
import io
import os
import json
import argparse
import sys
import re
from typing import Dict, List, Union, Optional, Any, Tuple
import logging
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# Setup logging
logger = logging.getLogger('bboxes')

class Settings(BaseSettings):
    """
    Application settings using pydantic for validation and secure handling of secrets.

    Attributes:
        GEMINI_API_KEY: Google Gemini API key stored as a SecretStr for security.
        GEMINI_MODEL: The Gemini model to use for image processing.
    """
    GEMINI_API_KEY: SecretStr
    GEMINI_MODEL: str = 'gemini-2.0-flash'

    # Use SettingsConfigDict instead of Config inner class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Allow extra fields in the settings
    )

def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging based on the verbose flag.

    Args:
        verbose: If True, enables DEBUG level logging. Otherwise, uses INFO level.
    """
    # Set log level based on verbose flag
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set our logger's level
    logger.setLevel(log_level)

    logger.debug("Debug logging enabled")
    logger.info("Logging initialized")

# Load settings with API key
settings = Settings()

# Configure Gemini with the API key from settings
try:
    genai.configure(api_key=settings.GEMINI_API_KEY.get_secret_value())
    logger.debug("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    print(f"Error: Failed to configure Gemini API. Please check your API key. Error: {e}")
    sys.exit(1)

def resolve_path(path: str) -> str:
    """
    Resolves a path string, handling relative paths, home directory expansion, etc.

    Expands common path formats:
    - Relative paths (./image.jpg, ../image.jpg)
    - Home directory paths (~/image.jpg)
    - Absolute paths (/path/to/image.jpg)

    Args:
        path: A file path string that may contain path shortcuts

    Returns:
        str: The resolved absolute path
    """
    # Expand user directory (handles ~ at the beginning of the path)
    expanded_path = os.path.expanduser(path)

    # Get the absolute path to resolve any relative paths like ./ or ../
    absolute_path = os.path.abspath(expanded_path)

    return absolute_path

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the bounding box script.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    # Create examples for the help text
    examples = """
Examples:
    # Basic usage with default parameters (tweet mode)
    # Output will be saved as input_filename_bbox.ext
    python bboxes.py --image-path "my_tweet.jpg"

    # Specify an image path and output
    python bboxes.py --image-path "my_tweet.jpg" --output-path "result.jpg"

    # Use general object detection mode
    python bboxes.py --mode "general" --image-path "photo.jpg"

    # Customize the bounding box
    python bboxes.py --image-path "tweet.png" --box-color "blue" --box-width 5 --label "Twitter Post"

    # Enable debug logging
    python bboxes.py --verbose --image-path "image.jpg"
    """

    parser = argparse.ArgumentParser(
        description="Detect objects or tweet content in images and draw bounding boxes",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--image-path", type=str, required=False,
        help="Path to the input image file"
    )
    parser.add_argument(
        "--output-path", type=str,
        help="Path to save the output image with bounding boxes"
    )
    parser.add_argument(
        "--mode", type=str, choices=["tweet", "general"], default="tweet",
        help="Detection mode: 'tweet' for tweet content or 'general' for all objects"
    )
    parser.add_argument(
        "--box-color", type=str, default="red",
        help="Color of the bounding box (name or hex code)"
    )
    parser.add_argument(
        "--box-width", type=int, default=4,
        help="Width of the bounding box line"
    )
    parser.add_argument(
        "--label", type=str,
        help="Custom label for the bounding box (tweet mode only)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose debug logging"
    )

    return parser.parse_args()

def detect_tweet_content(
    image_path: str,
    output_path: str = "tweet_with_box.jpg",
    box_color: str = "red",
    box_width: int = 4,
    label: Optional[str] = None
) -> None:
    """
    Detects tweet content in an image using Gemini, draws a bounding box, and saves the result.

    This function uses the Gemini generative model to identify tweet components in the
    provided image. It draws a red bounding box around the main tweet content (user profile,
    name, follow button, and tweet text), excluding date/time information and engagement
    metrics.

    Args:
        image_path: Path to the input image file containing a tweet.
        output_path: Path to save the output image with bounding box. Defaults to "tweet_with_box.jpg".
        box_color: Color of the bounding box (name or hex code). Defaults to "red".
        box_width: Width of the bounding box line. Defaults to 4.
        label: Custom label for the bounding box. Defaults to "Tweet Content".

    Returns:
        None

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        Exception: If there's an error processing the image or in the Gemini API.
    """
    try:
        logger.info(f"Detecting tweet content in {image_path}")
        logger.debug(f"Using box color: {box_color}, width: {box_width}, label: {label}")

        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.debug(f"Initialized Gemini model: {settings.GEMINI_MODEL}")

        img = PIL.Image.open(image_path)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        logger.debug(f"Image loaded and converted, size: {len(img_byte_arr)} bytes")

        img_part: Dict[str, Union[str, bytes]] = {"mime_type": "image/jpeg", "data": img_byte_arr}

        prompt_parts: List[Union[Dict[str, Union[str, bytes]], str]] = [
            img_part,
            """You're looking at a screenshot of a tweet. Create a precise bounding box around the MAIN TWEET CONTENT ONLY.

            The bounding box MUST include:
            1. The user's profile picture/avatar (usually circular)
            2. The username and @handle
            3. The "Follow" button
            4. The entire tweet text/content - CRITICALLY IMPORTANT TO INCLUDE ALL TEXT, INCLUDING ANY EMOJI OR SPECIAL CHARACTERS

            This is a single cohesive unit that forms the main tweet. Make sure the box captures ALL of this content.

            The bounding box MUST exclude:
            1. The navigation elements and header
            2. The date/timestamp
            3. Like/retweet/view counts and all engagement metrics
            4. Any replies or comments below the main tweet
            5. Any UI elements at the bottom of the screen

            IMPORTANT: Make sure your coordinates cover the ENTIRE tweet content from the profile picture to the end of the tweet text.
            When in doubt, make the bounding box LARGER rather than smaller to ensure no text is cut off.

            It is better to include a bit more space than to cut off any part of the text!

            Return only a JSON object with the exact coordinates as:
            {"xmin": [left coordinate], "ymin": [top coordinate], "xmax": [right coordinate], "ymax": [bottom coordinate]}

            The coordinates should be NORMALIZED to a range of 0-1000, where 0 represents the left/top edge and 1000 represents the right/bottom edge of the image."""
        ]

        logger.debug("Sending prompt to Gemini")
        response = model.generate_content(prompt_parts)
        response.resolve()
        logger.debug("Received response from Gemini")

        json_string: str = response.text
        logger.debug(f"Raw response: {json_string}")

        try:
            # Try to find the JSON object in the response text
            json_pattern = r'\{.*?\}'
            match = re.search(json_pattern, json_string, re.DOTALL)

            if match:
                json_string = match.group(0)
                logger.debug(f"Extracted JSON: {json_string}")

            # Clean up malformed JSON with square brackets around values
            json_string = re.sub(r'\[\s*(\d+)\s*\]', r'\1', json_string)
            logger.debug(f"Cleaned JSON: {json_string}")

            tweet_box: Dict[str, Any] = json.loads(json_string)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from Gemini: {json_string}")
            print(f"Error: Invalid JSON response from Gemini: {json_string}")

            # Attempt to manually extract coordinates if JSON parsing fails
            try:
                logger.debug("Attempting manual coordinate extraction")
                xmin_match = re.search(r'"xmin":\s*\[?(\d+)', json_string)
                ymin_match = re.search(r'"ymin":\s*\[?(\d+)', json_string)
                xmax_match = re.search(r'"xmax":\s*\[?(\d+)', json_string)
                ymax_match = re.search(r'"ymax":\s*\[?(\d+)', json_string)

                if all([xmin_match, ymin_match, xmax_match, ymax_match]):
                    tweet_box = {
                        'xmin': int(xmin_match.group(1)),
                        'ymin': int(ymin_match.group(1)),
                        'xmax': int(xmax_match.group(1)),
                        'ymax': int(ymax_match.group(1))
                    }
                    logger.debug(f"Manually extracted coordinates: {tweet_box}")
                else:
                    logger.error("Could not manually extract coordinates")
                    return
            except Exception as e:
                logger.exception(f"Failed to manually extract coordinates: {e}")
                return

        # Check if we have valid coordinates
        required_keys = ['xmin', 'ymin', 'xmax', 'ymax']
        if all(key in tweet_box for key in required_keys):
            xmin: float = float(tweet_box['xmin'])
            ymin: float = float(tweet_box['ymin'])
            xmax: float = float(tweet_box['xmax'])
            ymax: float = float(tweet_box['ymax'])

            logger.debug(f"Bounding box coordinates: xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}")

            # Validate coordinates
            if all(isinstance(coord, (int, float)) for coord in [xmin, ymin, xmax, ymax]):
                draw = PIL.ImageDraw.Draw(img)

                # Convert normalized coordinates (0-1000 range) to absolute pixel coordinates
                width, height = img.size
                abs_xmin = int(xmin / 1000 * width)
                abs_ymin = int(ymin / 1000 * height)
                abs_xmax = int(xmax / 1000 * width)
                abs_ymax = int(ymax / 1000 * height)
                logger.debug(f"Converted to absolute coordinates: xmin={abs_xmin}, ymin={abs_ymin}, xmax={abs_xmax}, ymax={abs_ymax}")

                # Add padding to ensure we capture all content
                # Horizontal padding (5% of width on each side)
                h_padding = int(width * 0.05)
                # Vertical padding (10% of detected height for bottom to ensure we capture all text)
                v_padding_top = int((abs_ymax - abs_ymin) * 0.05)
                v_padding_bottom = int((abs_ymax - abs_ymin) * 0.10)

                # Apply padding while ensuring we don't go out of bounds
                padded_xmin = max(0, abs_xmin - h_padding)
                padded_ymin = max(0, abs_ymin - v_padding_top)
                padded_xmax = min(width, abs_xmax + h_padding)
                padded_ymax = min(height, abs_ymax + v_padding_bottom)

                logger.debug(f"Added padding to coordinates: xmin={padded_xmin}, ymin={padded_ymin}, xmax={padded_xmax}, ymax={padded_ymax}")

                # Draw using padded coordinates
                draw.rectangle([(padded_xmin, padded_ymin), (padded_xmax, padded_ymax)], outline=box_color, width=box_width)

                # Use custom label or default
                box_label = label if label else "Tweet Content"
                draw.text((padded_xmin, padded_ymin - 20), box_label, fill=box_color)
                logger.debug(f"Drew bounding box with label: {box_label}")

                img.save(output_path)
                logger.info(f"Image with tweet content box saved to {output_path}")
                print(f"Image with tweet content box saved to {output_path}")
            else:
                logger.warning(f"Invalid bounding box coordinates: {tweet_box}")
                print(f"Warning: Invalid bounding box coordinates: {tweet_box}")
        else:
            logger.error(f"Missing required coordinates in response: {tweet_box}")
            print(f"Error: Missing required coordinates in response: {tweet_box}")

    except Exception as e:
        logger.exception(f"Error processing image: {e}")
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()

def detect_objects_and_draw_boxes(
    image_path: str,
    output_path: str = "output_with_boxes.jpg",
    box_color: str = "red",
    box_width: int = 3
) -> None:
    """
    Detects objects in an image using Gemini, draws bounding boxes, and saves the result.

    This function uses the Gemini generative model to identify objects in the provided
    image. It then draws red bounding boxes around each detected object, labels them,
    and saves the resulting image to the specified output path.

    Args:
        image_path: Path to the input image file.
        output_path: Path to save the output image with bounding boxes. Defaults to "output_with_boxes.jpg".
        box_color: Color of the bounding box (name or hex code). Defaults to "red".
        box_width: Width of the bounding box line. Defaults to 3.

    Returns:
        None

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        Exception: If there's an error processing the image or in the Gemini API.
    """
    try:
        logger.info(f"Detecting objects in {image_path}")
        logger.debug(f"Using box color: {box_color}, width: {box_width}")

        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.debug(f"Initialized Gemini model: {settings.GEMINI_MODEL}")

        img = PIL.Image.open(image_path)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        logger.debug(f"Image loaded and converted, size: {len(img_byte_arr)} bytes")

        img_part: Dict[str, Union[str, bytes]] = {"mime_type": "image/jpeg", "data": img_byte_arr}

        prompt_parts: List[Union[Dict[str, Union[str, bytes]], str]] = [
            img_part,
            "Identify and provide bounding box coordinates for all objects in the image. Return the results in JSON format. Each object should have 'label', 'xmin', 'ymin', 'xmax', and 'ymax' fields. The coordinates should be NORMALIZED to a range of 0-1000, where 0 represents the left/top edge and 1000 represents the right/bottom edge of the image. If there are no objects, return an empty JSON array. Example: [{'label': 'dog', 'xmin': 100, 'ymin': 200, 'xmax': 400, 'ymax': 600}, {'label': 'cat', 'xmin': 500, 'ymin': 300, 'xmax': 800, 'ymax': 700}]"
        ]

        logger.debug("Sending prompt to Gemini")
        response = model.generate_content(prompt_parts)
        response.resolve()
        logger.debug("Received response from Gemini")

        json_string: str = response.text
        logger.debug(f"Raw response: {json_string}")

        try:
            # Clean up malformed JSON with square brackets around values
            json_string = re.sub(r'\[\s*(\d+)\s*\]', r'\1', json_string)
            logger.debug(f"Cleaned JSON data: {json_string}")

            object_data: List[Dict[str, Any]] = json.loads(json_string)
            logger.debug(f"Parsed JSON data with {len(object_data)} objects")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from Gemini: {json_string}")
            print(f"Error: Invalid JSON response from Gemini: {json_string}")
            # No manual extraction for object detection as it's more complex
            return

        if isinstance(object_data, list):
            draw = PIL.ImageDraw.Draw(img)
            object_count = 0

            for obj in object_data:
                xmin: Optional[float] = obj.get('xmin')
                ymin: Optional[float] = obj.get('ymin')
                xmax: Optional[float] = obj.get('xmax')
                ymax: Optional[float] = obj.get('ymax')
                label: str = obj.get('label', 'Object')  # Default label if not present

                logger.debug(f"Processing object: {label} at coordinates: xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}")

                if all(isinstance(coord, (int, float)) for coord in [xmin, ymin, xmax, ymax]): #check if coordinates are valid numbers.
                    # Convert normalized coordinates (0-1000 range) to absolute pixel coordinates
                    width, height = img.size
                    abs_xmin = int(xmin / 1000 * width)
                    abs_ymin = int(ymin / 1000 * height)
                    abs_xmax = int(xmax / 1000 * width)
                    abs_ymax = int(ymax / 1000 * height)
                    logger.debug(f"Converted to absolute coordinates: xmin={abs_xmin}, ymin={abs_ymin}, xmax={abs_xmax}, ymax={abs_ymax}")

                    # Add padding to ensure we capture all content
                    # Horizontal padding (5% of width on each side)
                    h_padding = int(width * 0.03)
                    # Vertical padding (8% of detected height for top and bottom)
                    v_padding = int((abs_ymax - abs_ymin) * 0.08)

                    # Apply padding while ensuring we don't go out of bounds
                    padded_xmin = max(0, abs_xmin - h_padding)
                    padded_ymin = max(0, abs_ymin - v_padding)
                    padded_xmax = min(width, abs_xmax + h_padding)
                    padded_ymax = min(height, abs_ymax + v_padding)

                    logger.debug(f"Added padding to coordinates: xmin={padded_xmin}, ymin={padded_ymin}, xmax={padded_xmax}, ymax={padded_ymax}")

                    # Draw using padded coordinates
                    draw.rectangle([(padded_xmin, padded_ymin), (padded_xmax, padded_ymax)], outline=box_color, width=box_width)
                    draw.text((padded_xmin, padded_ymin - 10), label, fill=box_color) #draw the label above the bounding box.
                    object_count += 1
                    logger.debug(f"Drew bounding box for object: {label}")
                else:
                    logger.warning(f"Invalid bounding box coordinates for {label}: {obj}")
                    print(f"Warning: Invalid bounding box coordinates for {label}: {obj}")

            img.save(output_path)
            logger.info(f"Image with {object_count} bounding boxes saved to {output_path}")
            print(f"Image with bounding boxes saved to {output_path}")
        else:
            logger.error("Gemini returned results that are not a list")
            print("Gemini returned results that are not a list. Check the output.")

    except Exception as e:
        logger.exception(f"Error processing image: {e}")
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()

def main() -> int:
    """
    Main function to process images and draw bounding boxes.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    args = parse_args()

    # Set up logging based on verbose flag
    setup_logging(args.verbose)

    logger.info("Starting bounding box detection")
    logger.debug(f"Arguments: {args}")

    # Default image path if not provided
    image_file = args.image_path or "tweet_screenshot.jpg"

    # Resolve path to handle relative paths, home directory paths, etc.
    image_path = resolve_path(image_file)

    logger.debug(f"Using image file: {image_path}")

    if not os.path.exists(image_path):
        logger.error(f"Image file '{image_path}' not found")
        print(f"Error: Image file '{image_path}' not found.")
        return 1

    # Generate default output path based on input filename if not provided
    if args.output_path:
        output_file = args.output_path
    else:
        # Split the image path into directory, filename, and extension
        input_dir = os.path.dirname(image_path)
        input_basename = os.path.basename(image_path)
        input_name, input_ext = os.path.splitext(input_basename)

        # Create default output filename by adding _bbox before the extension
        default_output_name = f"{input_name}_bbox{input_ext}"

        # Combine with the original directory to keep in same location
        output_file = os.path.join(input_dir, default_output_name)

        logger.debug(f"Generated default output path: {output_file}")

    # Resolve the output path
    output_path = resolve_path(output_file)
    logger.debug(f"Resolved output path: {output_path}")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            logger.error(f"Error creating output directory: {e}")
            print(f"Error creating output directory: {e}")
            return 1

    try:
        if args.mode == "tweet":
            logger.info("Using tweet content detection mode")
            detect_tweet_content(
                image_path,
                output_path,
                box_color=args.box_color,
                box_width=args.box_width,
                label=args.label
            )
        else:  # general mode
            logger.info("Using general object detection mode")
            detect_objects_and_draw_boxes(
                image_path,
                output_path,
                box_color=args.box_color,
                box_width=args.box_width
            )
        logger.info("Processing completed successfully")
        return 0
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
