import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import os
import plistlib
import json

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        
        # Variables
        self.current_image = None
        self.photo = None
        self.plist_data = None
        self.canvas_width = 0
        self.canvas_height = 0
        
        # Make window unresizable
        self.root.resizable(False, False)
        
        # Create canvas to display image
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
    def load_image(self, filename):
        """Load and display the image, scaling down if larger than screen"""
        # Open image with PIL
        self.current_image = Image.open(filename)
        
        # Get image dimensions
        img_width, img_height = self.current_image.size
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Leave some margin for window decorations and taskbar
        max_width = screen_width - 100
        max_height = screen_height - 100
        
        # Check if image needs to be scaled down
        if img_width > max_width or img_height > max_height:
            # Calculate scaling factor to fit within screen while maintaining aspect ratio
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            display_width = int(img_width * scale_factor)
            display_height = int(img_height * scale_factor)
            
            # Resize image
            display_image = self.current_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        else:
            # Use original image if it fits on screen
            display_image = self.current_image
            display_width = img_width
            display_height = img_height
        
        # Set window size to match display size
        self.root.geometry(f"{display_width}x{display_height}")
        
        # Configure canvas size and store dimensions
        self.canvas.config(width=display_width, height=display_height)
        self.canvas_width = display_width
        self.canvas_height = display_height
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(
            0, 0, 
            anchor=tk.NW, 
            image=self.photo
        )
        
        # Update window title to include filename and scaling info
        filename_only = os.path.basename(filename)
        if display_width != img_width or display_height != img_height:
            self.root.title(f"Image Viewer - {filename_only} (scaled to fit screen)")
        else:
            self.root.title(f"Image Viewer - {filename_only} (native size)")
    
    def draw_button_models(self):
        """Draw circles on the canvas based on buttonModels data"""
        if not self.plist_data or 'buttonModels' not in self.plist_data:
            return
        
        button_models = self.plist_data['buttonModels']
        if not isinstance(button_models, list):
            return
        
        for button in button_models:
            if not isinstance(button, dict) or 'transform' not in button:
                continue
            
            transform = button['transform']
            if not isinstance(transform, dict):
                continue
            
            # Get transform values with defaults
            size = transform.get('size', 5.0)
            x_coord = transform.get('xCoord', 0.0)
            y_coord = transform.get('yCoord', 0.0)
            
            # Calculate circle properties
            diameter = (size / 100) * self.canvas_width
            radius = diameter / 2
            center_x = x_coord * self.canvas_width
            center_y = y_coord * self.canvas_height
            
            # Calculate circle bounds
            x1 = center_x - radius
            y1 = center_y - radius
            x2 = center_x + radius
            y2 = center_y + radius
            
            # Draw circle (outline only for visibility)
            self.canvas.create_oval(
                x1, y1, x2, y2,
                outline='red',
                width=2,
                fill='',
                tags='button_circle'
            )
            
            # Optionally draw key name if available
            key_name = button.get('keyName', '')
            if key_name:
                self.canvas.create_text(
                    center_x, center_y,
                    text=key_name,
                    fill='red',
                    font=('Arial', 10, 'bold'),
                    tags='button_text'
                )
    
    def load_plist(self, filename):
        """Load and parse a plist file"""
        try:
            with open(filename, 'rb') as plist_file:
                self.plist_data = plistlib.load(plist_file)
            
            # Create a new window for displaying the plist content
            data_window = tk.Toplevel(self.root)
            data_window.title("Data Viewer")
            data_window.geometry("800x600")
            data_window.resizable(True, True)
            
            # Create a frame for the text widget and scrollbar
            text_frame = tk.Frame(data_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create text widget with scrollbar
            text_widget = tk.Text(
                text_frame, 
                wrap=tk.WORD, 
                font=('Consolas', 12),
                bg='white',
                fg='black'
            )
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_widget.yview)
            
            # Format and display the plist data as JSON for better readability
            formatted_content = json.dumps(self.plist_data, indent=2, default=str)
            text_widget.insert(tk.END, formatted_content)
            text_widget.config(state=tk.DISABLED)  # Make it read-only
            
            # Update window title
            filename_only = os.path.basename(filename)
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == '.playmap':
                data_window.title(f"Playmap Viewer - {filename_only}")
            else:
                data_window.title(f"Plist Viewer - {filename_only}")
            
            return self.plist_data
            
        except Exception as e:
            raise Exception(f"Failed to parse plist file: {str(e)}")
    
    def load_json(self, filename):
        """Load and parse a JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as json_file:
                self.plist_data = json.load(json_file)
            
            # Create a new window for displaying the JSON content
            data_window = tk.Toplevel(self.root)
            data_window.title("Data Viewer")
            data_window.geometry("800x600")
            data_window.resizable(True, True)
            
            # Create a frame for the text widget and scrollbar
            text_frame = tk.Frame(data_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create text widget with scrollbar
            text_widget = tk.Text(
                text_frame, 
                wrap=tk.WORD, 
                font=('Consolas', 12),
                bg='white',
                fg='black'
            )
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_widget.yview)
            
            # Format and display the JSON data with proper indentation
            formatted_content = json.dumps(self.plist_data, indent=2, default=str)
            text_widget.insert(tk.END, formatted_content)
            text_widget.config(state=tk.DISABLED)  # Make it read-only
            
            # Update window title
            filename_only = os.path.basename(filename)
            data_window.title(f"JSON Viewer - {filename_only}")
            
            return self.plist_data
            
        except Exception as e:
            raise Exception(f"Failed to parse JSON file: {str(e)}")

def main():
    root = tk.Tk()
    app = ImageViewer(root)
    
    # Hide the window initially
    root.withdraw()
    
    # First popup: Select an image file
    image_file_types = [
        ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.tif'),
        ('PNG files', '*.png'),
        ('JPEG files', '*.jpg *.jpeg'),
        ('GIF files', '*.gif'),
        ('BMP files', '*.bmp'),
        ('TIFF files', '*.tiff *.tif'),
        ('All files', '*.*')
    ]
    
    image_filename = filedialog.askopenfilename(
        title="First: Select an image file to view",
        filetypes=image_file_types
    )
    
    if not image_filename:
        # User cancelled image selection, exit
        root.quit()
        return
    
    # Second popup: Select a plist or JSON file
    data_file_types = [
        ('Data files', '*.plist *.json *.playmap'),
        ('Plist files', '*.plist'),
        ('JSON files', '*.json'),
        ('Playmap files', '*.playmap'),
        ('All files', '*.*')
    ]
    
    data_filename = filedialog.askopenfilename(
        title="Second: Select a plist, JSON, or playmap file to view",
        filetypes=data_file_types
    )
    
    if not data_filename:
        # User cancelled data file selection, exit
        root.quit()
        return
    
    # Show the window and load both files
    root.deiconify()
    
    try:
        # Load and display the image first
        app.load_image(image_filename)
        
        # Load and display the data file in a separate window
        file_ext = os.path.splitext(data_filename)[1].lower()
        
        if file_ext in ['.plist', '.playmap']:
            data = app.load_plist(data_filename)
        elif file_ext == '.json':
            data = app.load_json(data_filename)
        else:
            # Try to load as JSON first, then plist if that fails
            try:
                data = app.load_json(data_filename)
            except:
                data = app.load_plist(data_filename)
        
        # Draw button models on the image canvas
        app.draw_button_models()
        
        # Print the loaded data to console for programmatic access
        print("Loaded data:")
        print(json.dumps(data, indent=2, default=str))
        
    except Exception as e:
        messagebox.showerror(
            "Error", 
            f"Failed to load files:\n{str(e)}"
        )
        root.quit()
        return
    
    root.mainloop()

if __name__ == "__main__":
    main()