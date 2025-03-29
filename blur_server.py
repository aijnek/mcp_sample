import os
from mcp.server.fastmcp import FastMCP
from PIL import Image as PILImage, ImageFilter
from facenet_pytorch import MTCNN

mcp = FastMCP("FaceBlur")
mtcnn = MTCNN(keep_all=True, device="cpu")

@mcp.tool()
def create_thumbnail(image_path: str, save_path: str = None) -> str:
    """Creates and saves a thumbnail from the specified image path.

    Args:
        image_path: Path to the original image to create a thumbnail from.
        save_path: Path to save the thumbnail. If not specified, '_thumbnail'
                   will be appended to the original filename.

    Returns:
        A message indicating the path where the thumbnail was saved, or an error message.
    """
    try:
        img = PILImage.open(image_path)
        img.thumbnail((100, 100))
        if save_path:
            thumbnail_path = save_path
        else:
            base, ext = os.path.splitext(image_path)
            base += f"_thumbnail"
            thumbnail_path = f"{base}{ext}"
        img.save(thumbnail_path)
        return f"Thumbnail saved to {thumbnail_path}"
    except Exception as e:
        return f"Error creating thumbnail: {e}"

@mcp.tool()
def detect_faces(image_path: str) -> str:
    """Detects faces in the specified image and returns their bounding boxes.

    Args:
        image_path: Path to the image to detect faces in.

    Returns:
        A message with the detected face bounding boxes or an error message.
    """
    try:
        img = PILImage.open(image_path)
        img = img.convert('RGB')
        width, height = img.size # 画像の幅と高さを取得
        boxes, _ = mtcnn.detect(img)
        if boxes is not None:
            # 相対座標に変換
            relative_boxes = []
            for box in boxes:
                xmin, ymin, xmax, ymax = box
                relative_boxes.append([
                    round(xmin / width, 2),
                    round(ymin / height, 2),
                    round(xmax / width, 2),
                    round(ymax / height, 2)
                ])
            return f"Detected faces: {relative_boxes}" # 変換後のリストを返す
        else:
            return "No faces detected."
    except Exception as e:
        return f"Error detecting faces: {e}"

@mcp.tool()
def blur(image_path: str, xmin: float, ymin: float, xmax: float, ymax: float, save_path: str = None) -> str:
    """Blurs a specified rectangular region within an image and saves the result.

    Args:
        image_path: Path to the original image to apply blur to.
        xmin: Normalized minimum x-coordinate (0.0-1.0) of the blur region.
        ymin: Normalized minimum y-coordinate (0.0-1.0) of the blur region.
        xmax: Normalized maximum x-coordinate (0.0-1.0) of the blur region.
        ymax: Normalized maximum y-coordinate (0.0-1.0) of the blur region.
        save_path: Path to save the blurred image. If not specified, '_blur'
                   will be appended to the original filename (saved as PNG).

    Returns:
        A message indicating the path where the blurred image was saved, or an error message.
    """
    try:
        img = PILImage.open(image_path).convert("RGBA") # Convert to RGBA to handle transparency
        width, height = img.size

        # Convert normalized coordinates to pixel coordinates
        xmin_px = int(xmin * width)
        ymin_px = int(ymin * height)
        xmax_px = int(xmax * width)
        ymax_px = int(ymax * height)

        # Ensure coordinates are within image bounds
        xmin_px = max(0, xmin_px)
        ymin_px = max(0, ymin_px)
        xmax_px = min(width, xmax_px)
        ymax_px = min(height, ymax_px)

        # Check if the region is valid (positive width and height)
        if xmax_px <= xmin_px or ymax_px <= ymin_px:
            # If the region is invalid, maybe just save the original image or return an error/warning?
            # For now, let's proceed but the blur won't be applied effectively.
            # Alternatively, could return a specific message:
            # return f"Warning: Invalid blur region specified ({xmin_px}, {ymin_px}, {xmax_px}, {ymax_px}). Original image saved."
            pass # Proceed to save, but no blur applied if region is invalid

        # Crop the specified region if valid
        if xmax_px > xmin_px and ymax_px > ymin_px:
            region = img.crop((xmin_px, ymin_px, xmax_px, ymax_px))

            # Blur the cropped region (adjust GaussianBlur radius as needed)
            blurred_region = region.filter(ImageFilter.GaussianBlur(radius=10))

            # Paste the blurred region back onto the original image
            img.paste(blurred_region, (xmin_px, ymin_px))

        # Set the save path
        if save_path:
            blur_path = save_path
        else:
            base, ext = os.path.splitext(image_path)
            base += f"_blur"
            blur_path = f"{base}{ext}" # Initial path with original extension

        # Ensure saving in a format that supports RGBA (like PNG)
        if not blur_path.lower().endswith(('.png', '.gif', '.tiff', '.webp')):
             base, _ = os.path.splitext(blur_path)
             blur_path = f"{base}.png" # Change extension to PNG for safety

        img.save(blur_path, format='PNG') # Save explicitly as PNG

        return f"Blurred image saved to {blur_path}"
    except FileNotFoundError:
        return f"Error: Image file not found ({image_path})"
    except Exception as e:
        return f"Error applying blur: {e}"

if __name__ == "__main__":
    mcp.run(transport="stdio")