import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, Label, Button, Frame, Toplevel
from PIL import Image, ImageTk
from tkinter import ttk

# Function to load an image through the file dialog
def load_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        if image is None:
            print(f"Error: Unable to load the image from {file_path}")
        return image, file_path
    return None, None

# Function to calculate automatic brightness and contrast adjustments
def automatic_brightness_contrast(image, clip_hist_percent=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    accumulator = np.cumsum(hist)

    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left and right cut
    minimum_gray = np.where(accumulator > clip_hist_percent)[0][0]
    maximum_gray = np.where(accumulator >= (maximum - clip_hist_percent))[0][0]

    # Calculate alpha and beta values
    alpha = 255.0 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return auto_result, alpha, beta

# Function to apply Gaussian filter for noise reduction
def apply_gaussian_filter(image):
    return cv2.GaussianBlur(image, (5, 5), 0)

# Function to apply Laplace operator for edge sharpening (with blending)
def apply_laplace_operator(image):
    laplace = cv2.Laplacian(image, cv2.CV_64F)
    laplace_abs = cv2.convertScaleAbs(laplace)
    return cv2.addWeighted(image, 0.8, laplace_abs, 0.2, 0)

# Function to update the UI with the enhanced image
def enhance_image():
    global img_label, image

    # Step 1: Load the image
    image, image_path = load_image()
    if image is None:
        return

    # Step 2: Automatically adjust brightness and contrast
    enhanced_image, _, _ = automatic_brightness_contrast(image)

    # Step 3: Apply Gaussian filter and Laplacian for sharpening
    smoothed_image = apply_gaussian_filter(enhanced_image)
    final_image = apply_laplace_operator(smoothed_image)

    # Convert the image to a format Tkinter can display
    img_rgb = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)

    # Update label with new image
    img_label.configure(image=img_tk)
    img_label.image = img_tk  # Keep reference to avoid garbage collection

# Function to save the enhanced image
def save_image():
    if image is not None:
        # Save the enhanced image to disk
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            cv2.imwrite(file_path, image)

# Create the Tkinter window
window = tk.Tk()
window.title("Oil Painting Image Enhancer Tool")
window.geometry("1000x700")


# Load the background image
background_image = Image.open(r'C:\Users\HP\Desktop\ivp\Images\four.jpg')  # Replace with your image file path
background_image = background_image.resize((1000, 700), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
bg_img_tk = ImageTk.PhotoImage(background_image)


# Create a Canvas widget and set the background image
canvas = tk.Canvas(window, width=1000, height=700)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_img_tk, anchor="nw")

# Title label
title_label = Label(window, text="Oil Painting Image Enhancer", font=("Arial", 30, "bold"), bg='#f0f0f0', fg='#333')
title_label_window = canvas.create_window(500, 50, window=title_label)  # Positioned using canvas

# Frame to contain buttons and image
frame = Frame(window, bg='#f0f0f0')
frame_window = canvas.create_window(500, 400, window=frame)

# Button to upload and enhance the image
upload_button = Button(frame, text="Upload and Enhance Image", command=enhance_image, font=("Arial", 14), bg='#333', fg='white', padx=20, pady=10, relief='flat')
upload_button.grid(row=0, column=0, padx=20, pady=10)

# Image label (empty initially)
img_label_frame = Frame(frame, width=600, height=400, bg='white', highlightbackground="black", highlightthickness=2)
img_label_frame.grid(row=1, column=0, pady=20)
img_label = Label(img_label_frame, bg='white')
img_label.pack(expand=True, fill=tk.BOTH)

# Button to save the enhanced image
save_button = Button(frame, text="Save Enhanced Image", command=save_image, font=("Arial", 14), bg='#333', fg='white', padx=20, pady=10, relief='flat')
save_button.grid(row=2, column=0, padx=20, pady=10)

# Start the Tkinter event loop
window.mainloop()
