import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

class GridImageSelector:
    def __init__(self, image_path, grid_size):
        self.image_path = image_path
        self.grid_size = grid_size
        self.selected_squares = []

        # Load the image
        self.original_image = Image.open(self.image_path)
        self.image_width, self.image_height = self.original_image.size

        # Create a Tkinter window
        self.root = tk.Tk()
        self.root.title("Grid Image Selector")

        # Create a frame to hold the canvas and scrollbar
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas to display the image with scrollbars
        self.canvas = tk.Canvas(self.canvas_frame, width=self.image_width, height=self.image_height)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create vertical and horizontal scrollbars
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.config(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.config(xscrollcommand=self.h_scrollbar.set)

        # Make the canvas scrollable by configuring grid weights
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Draw the grid on the image
        self.draw_grid()

        # Bind the click event
        self.canvas.bind("<Button-1>", self.on_click)

        self.matrix = []
        for i in range(27):
            row = []
            for j in range(48):
                row.append(1)
            self.matrix.append(row)

        # Start the Tkinter main loop
        self.root.mainloop()



    def draw_grid(self):
        # Create a copy of the image to draw on
        self.image_with_grid = self.original_image.copy()
        draw = ImageDraw.Draw(self.image_with_grid)

        # Draw the grid lines
        for x in range(0, self.image_width, self.grid_size):
            draw.line((x, 0, x, self.image_height), fill="black")
        for y in range(0, self.image_height, self.grid_size):
            draw.line((0, y, self.image_width, y), fill="black")

        # Convert the image to a format Tkinter can use
        self.tk_image = ImageTk.PhotoImage(self.image_with_grid)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Configure the scroll region to allow scrolling of the full image
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_click(self, event):
        # Adjust the click coordinates for scrolling
        canvas_x = self.canvas.canvasx(event.x)  # Get the real x-coordinate considering scrolling
        canvas_y = self.canvas.canvasy(event.y)  # Get the real y-coordinate considering scrolling

        # Calculate the grid square that was clicked
        grid_x = canvas_x // self.grid_size
        grid_y = canvas_y // self.grid_size
        square = (grid_x, grid_y)

        # Print the selected squares
        print("Selected squares:", self.selected_squares)
        c, r = square
        self.matrix[int(r)][int(c)] = 1 if self.matrix[int(r)][int(c)] == 0 else 0
        print(self.matrix, "\n"*10)

        # Toggle the selection of the square
        if square in self.selected_squares:
            self.selected_squares.remove(square)
            self.highlight_square(grid_x, grid_y, remove=True)
        else:
            self.selected_squares.append(square)
            self.highlight_square(grid_x, grid_y)

    def highlight_square(self, grid_x, grid_y, remove=False):
        # Calculate the pixel coordinates of the square
        x1 = grid_x * self.grid_size
        y1 = grid_y * self.grid_size
        x2 = x1 + self.grid_size
        y2 = y1 + self.grid_size

        # Draw or remove the highlight
        if remove:
            color = "white"
        else:
            color = "red"

        # Draw the rectangle
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

if __name__ == "__main__":
    # Path to the image file
    image_path = "/Users/air/Desktop/FDJ/werian/assets/td-tilesets1-2/tower-defense-game-tilesets/PNG/game_background_3/game_background_3.png"

    # Size of each grid square in pixels
    grid_size = 40

    # Create and run the grid image selector
    g = GridImageSelector(image_path, grid_size)