import math
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import simpledialog, colorchooser
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# Define set_params function
def set_params(name, birthday, color1, color2, color3, color4, color5, color6):
    # Extracting DD, MM, YY values from the birthday input
    components = [int(component) for component in birthday.split(',')]

    # If there is only one component, assume it's the day (DD)
    if len(components) == 1:
        dd, mm, yy = components[0], 1, 1
    # If there are two components, assume they are day and month (DD, MM)
    elif len(components) == 2:
        dd, mm, yy = components[0], components[1], 1
    # If there are three components, assume they are day, month, and year (DD, MM, YY)
    elif len(components) == 3:
        dd, mm, yy = components[0], components[1], components[2]
    else:
        raise ValueError("Invalid birthday format")

    # Calculating stripe sizes based on DD, MM, YY values
    stripe_sizes = [dd, mm, yy]
    
    # Fixed width and height to 500x500 = works the best
    width, height = 500, 500

    # Fixed scale factor - gets a larger range of grid sizes, don't know why
    scale_factor = 15
    
    # Convert color hex strings to RGB tuples
    color1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
    color2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
    color3 = tuple(int(color3[i:i+2], 16) for i in (1, 3, 5))
    color4 = tuple(int(color4[i:i+2], 16) for i in (1, 3, 5))
    color5 = tuple(int(color5[i:i+2], 16) for i in (1, 3, 5))
    color6 = tuple(int(color6[i:i+2], 16) for i in (1, 3, 5))

    return name, width, height, scale_factor, [(255, 0, 0), color1, color2], [(0, 0, 255), color3, color4], stripe_sizes


# Create image
def create_image(width: int, height: int):
    img = Image.new('RGB', (width, height))
    return img

# Choose orientation
def choose_orientation(w_ind, h_ind) -> str:
    w_rem = w_ind % 4
    h_rem = h_ind % 4
    if (w_rem == h_rem or w_rem == h_rem + 1):
        return "horz"
    else:
        return "vert"

# Choose color
def choose_color(v_pattern, h_pattern, w_ind, h_ind, w, h, stripe_sizes):
    orientation = choose_orientation(w, h)

    pattern = v_pattern if orientation == "vert" else h_pattern
    ind = w_ind if orientation == "vert" else h_ind
    
    # Use the sum of birthday components as the size of the stripe
    stripe_size = stripe_sizes[ind % len(stripe_sizes)]
    
    return pattern[ind % len(pattern)], stripe_size

# Colorize image
def colorize_image(img, horz_pattern, vert_pattern, scale_factor, stripe_sizes):
    width, height = img.size
    print("Width: {} | Height: {} | Scale Factor: {}"
        .format(width, height, scale_factor))
    print("Horz Pattern: {}".format(horz_pattern))
    print("Vert Pattern: {}".format(vert_pattern))
    
    # Pattern and scaling factor for tartan-like stripes
    for w in range(width):
        for h in range(height):
            w_floor = math.floor(w / scale_factor)
            h_floor = math.floor(h / scale_factor)
            color, stripe_size = choose_color(vert_pattern, horz_pattern, w_floor, h_floor, w, h, stripe_sizes)
            
            # Draw stripe by checking if pixel index is within the stripe size
            if (w % scale_factor) < stripe_size and (h % scale_factor) < stripe_size:
                img.putpixel((w, h), color)

# Get color dictionary
def get_color_dict():
    color_dict = {
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "green": (0, 255, 0),
        "white": (255, 255, 255),
        "gray": (150, 150, 150),
        "tan": (194, 158, 114)
    }
    return color_dict

# Generate tartan
def generate_tartan(name, birthday, color1, color2, color3, color4, color5, color6):
    name, width, height, scale_factor, horz_pattern, vert_pattern, stripe_sizes = set_params(name, birthday, color1, color2, color3, color4, color5, color6)
    img = create_image(width, height)
    colorize_image(img, horz_pattern, vert_pattern, scale_factor, stripe_sizes)

    # Save the generated image in the "datatartandatabase" folder with the specified name
    folder_path = "static/datatartandatabase"
    os.makedirs(folder_path, exist_ok=True)
    img_path = os.path.join(folder_path, f"{name}_tartan.png")
    img.save(img_path)

    return img_path
# Flask routes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs from the form
        name = request.form['name']
        birthday = request.form['birthday']
        color1 = request.form['color1']
        color2 = request.form['color2']
        color3 = request.form['color3']
        color4 = request.form['color4']
        color5 = request.form['color5']
        color6 = request.form['color6']

        # Call the generate_tartan function and get the file path
        file_path = generate_tartan(name, birthday, color1, color2, color3, color4, color5, color6)

        # Return the file path or binary data
        return send_file(file_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)