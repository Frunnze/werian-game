from PIL import Image, ImageDraw
from PIL import Image, ImageDraw, ImageFont

def draw_grid_with_indices(image_path, output_path, grid_size=(40, 40), font_path=None, font_size=50):
    """
    Draws a grid over the input image with indices and saves the output.

    :param image_path: Path to the input image
    :param output_path: Path to save the output image
    :param grid_size: Tuple (grid_width, grid_height) representing the size of grid cells
    :param font_path: Path to a .ttf font file (optional, uses default font if None)
    :param font_size: Font size for indices
    """
    # Open the input image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Get image dimensions
    img_width, img_height = image.size
    print(img_width, img_height)

    # Unpack grid size
    grid_width, grid_height = grid_size
    print(img_width/40, img_height/40)

    # Load the font (default to a system font if no font is provided)
    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception as e:
        print(f"Could not load font: {e}")
        font = ImageFont.load_default()

    # Draw vertical grid lines and row-column indices
    for col in range(0, img_width, grid_width):
        for row in range(0, img_height, grid_height):
            # Calculate cell top-left corner
            x, y = col, row
            
            # Draw the grid cell
            draw.rectangle([x, y, x + grid_width, y + grid_height], outline="red", width=1)

            # Draw the indices (row, col)
            text = f"{row // grid_height},{col // grid_width}"
            text_position = (x + 5, y + 5)  # Offset slightly for padding
            draw.text(text_position, text, fill="white", font=font)

    # Save the output image
    image.save(output_path)
    print(f"Grid with indices drawn and saved to {output_path}")

# Example usage
input_image = "game_background_3.png"  # Replace with your image file
output_image = "output_with_grid.jpg"

draw_grid_with_indices(input_image, output_image)