import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os
import plistlib
import json

CodeToKeys = {
    -4: "cA",
    -5: "cX",
    -6: "cB",
    -7: "cY",
    -8: "dU",
    -9: "dD",
    -10: "Controller",
    -11: "dL",
    -12: "L1",
    -13: "L2",
    -14: "R1",
    -15: "R2",
    -1: "LMB",
    -2: "RMB",
    -3: "MMB",
    41: "Escape",
    44: "space",
    225: "Shift_L",
    57: "Caps_Lock",
    43: "Tab",
    227: "Super_L",
    226: "Alt_L",
    231: "Super_R",
    230: "Alt_R",
    40: "Return",
    42: "BackSpace",
    229: "Shift_R",
    80: "Left",
    79: "Right",
    82: "Up",
    81: "Down",
    58: "F1",
    59: "F2",
    60: "F3",
    61: "F4",
    62: "F5",
    63: "F6",
    64: "F7",
    65: "F8",
    66: "F9",
    67: "F10",
    68: "F11",
    69: "F12",
    100: "section",
    30: "1",
    31: "2",
    32: "3",
    33: "4",
    34: "5",
    35: "6",
    36: "7",
    37: "8",
    38: "9",
    39: "0",
    45: "minus",
    46: "equal",
    20: "q",
    26: "w",
    8: "e",
    21: "r",
    23: "t",
    28: "y",
    24: "u",
    12: "i",
    18: "o",
    19: "p",
    47: "bracketleft",
    48: "bracketright",
    4: "a",
    22: "s",
    7: "d",
    9: "f",
    10: "g",
    11: "h",
    13: "j",
    14: "k",
    15: "l",
    51: "semicolon",
    52: "apostrophe",
    49: "backslash",
    29: "z",
    53: "grave",
    27: "x",
    6: "c",
    25: "v",
    5: "b",
    17: "n",
    16: "m",
    54: "comma",
    55: "period",
    56: "slash",
}

KeyToCode = {v: k for k, v in CodeToKeys.items()}

KeyNameDifferences = {
    "Escape": "Esc",
    "space": "Spc",
    "Shift_L": "Lshft",
    "Caps_Lock": "Caps",
    "Super_L": "LCmd",
    "Alt_L": "LOpt",
    "Super_R": "RCmd",
    "Alt_R": "ROpt",
    "Return": "Enter",
    "BackSpace": "Del",
    "Shift_R": "Rshft",
    "section": "§",
    "minus": "-",
    "equal": "=",
    "q": "Q",
    "w": "W",
    "e": "E",
    "r": "R",
    "t": "T",
    "y": "Y",
    "u": "U",
    "i": "I",
    "o": "O",
    "p": "P",
    "bracketleft": "[",
    "bracketright": "]",
    "a": "A",
    "s": "S",
    "d": "D",
    "f": "F",
    "g": "G",
    "h": "H",
    "j": "J",
    "k": "K",
    "l": "L",
    "semicolon": ";",
    "apostrophe": "'",
    "backslash": "\\",
    "z": "Z",
    "grave": "`",
    "x": "X",
    "c": "C",
    "v": "V",
    "b": "B",
    "n": "N",
    "m": "M",
    "comma": ",",
    "period": ".",
    "slash": "/",
}


def is_image_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif"
    ]


def is_plist_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in [".plist", ".playmap"]


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
        self.dragging_item = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.button_circles = {}  # Store circle IDs and their corresponding button data
        self.save_window = None  # Store reference to save window

        # Make window unresizable
        self.root.resizable(False, False)

        # Bind close event to exit program
        self.root.protocol("WM_DELETE_WINDOW", self.on_main_window_close)

        # Create canvas to display image
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events for dragging
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

    def on_main_window_close(self):
        """Handle main window close event"""
        self.root.quit()

    def on_save_window_close(self):
        """Handle save window close event"""
        self.root.quit()

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
            display_image = self.current_image.resize(
                (display_width, display_height), Image.Resampling.LANCZOS
            )
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
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Update window title to include filename and scaling info
        filename_only = os.path.basename(filename)
        if display_width != img_width or display_height != img_height:
            self.root.title(f"Image Viewer - {filename_only} (scaled to fit screen)")
        else:
            self.root.title(f"Image Viewer - {filename_only} (native size)")

    def draw_button_models(self):
        """Draw circles on the canvas based on buttonModels data"""
        if not self.plist_data or "buttonModels" not in self.plist_data:
            return

        button_models = self.plist_data["buttonModels"]
        if not isinstance(button_models, list):
            return

        # Clear existing button circles and text, but preserve the background image
        self.canvas.delete("button_circle")
        self.canvas.delete("button_text")
        self.button_circles = {}  # Clear existing mappings

        for i, button in enumerate(button_models):
            if not isinstance(button, dict) or "transform" not in button:
                continue

            transform = button["transform"]
            if not isinstance(transform, dict):
                continue

            # Get transform values with defaults
            size = transform.get("size", 5.0)
            x_coord = transform.get("xCoord", 0.0)
            y_coord = transform.get("yCoord", 0.0)

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
            circle_id = self.canvas.create_oval(
                x1, y1, x2, y2, outline="red", width=2, fill="", tags="button_circle"
            )

            # Draw key name if available - use original keyName from the file
            key_name = button.get("keyName", "")

            text_id = None
            if key_name:
                text_id = self.canvas.create_text(
                    center_x,
                    center_y,
                    text=key_name,
                    fill="red",
                    font=("Arial", 14, "bold"),
                    tags="button_text",
                )

            # Store the mapping between circle ID and button data
            self.button_circles[circle_id] = {
                "button_index": i,
                "text_id": text_id,
                "button_data": button,
            }

    def on_click(self, event):
        """Handle mouse click events"""
        # Find the closest item to the click
        item = self.canvas.find_closest(event.x, event.y)[0]

        # Get tags safely
        tags = self.canvas.gettags(item)

        # Check if it's a button circle or text
        if item in self.button_circles or (
            tags and tags[0] in ["button_circle", "button_text"]
        ):
            # If it's text, find the corresponding circle
            if tags and tags[0] == "button_text":
                # Find the circle that corresponds to this text
                for circle_id, data in self.button_circles.items():
                    if data["text_id"] == item:
                        item = circle_id
                        break

            if item in self.button_circles:
                self.dragging_item = item
                self.drag_start_x = event.x
                self.drag_start_y = event.y

    def on_drag(self, event):
        """Handle mouse drag events"""
        if self.dragging_item:
            # Calculate the offset
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y

            # Move the circle
            self.canvas.move(self.dragging_item, dx, dy)

            # Move the corresponding text if it exists
            circle_data = self.button_circles[self.dragging_item]
            if circle_data["text_id"]:
                self.canvas.move(circle_data["text_id"], dx, dy)

            # Update the drag start position
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def on_release(self, event):
        """Handle mouse release events"""
        if self.dragging_item:
            # Update the button data with new coordinates
            circle_data = self.button_circles[self.dragging_item]

            # Get the current position of the circle
            coords = self.canvas.coords(self.dragging_item)
            center_x = (coords[0] + coords[2]) / 2
            center_y = (coords[1] + coords[3]) / 2

            # Convert back to normalized coordinates
            new_x_coord = center_x / self.canvas_width
            new_y_coord = center_y / self.canvas_height

            # Update the button data
            button_index = circle_data["button_index"]
            self.plist_data["buttonModels"][button_index]["transform"][
                "xCoord"
            ] = new_x_coord
            self.plist_data["buttonModels"][button_index]["transform"][
                "yCoord"
            ] = new_y_coord

            self.dragging_item = None

    def create_save_window(self, filename):
        """Create a simple save window with save and add button"""
        # Create a new window for the controls
        self.save_window = tk.Toplevel(self.root)
        self.save_window.title("Controls")
        self.save_window.geometry("150x200")
        self.save_window.resizable(False, False)

        # Bind close event to exit program
        self.save_window.protocol("WM_DELETE_WINDOW", self.on_save_window_close)

        # Create a frame for the content
        content_frame = tk.Frame(self.save_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Add "Change Image" button
        change_image_button = tk.Button(
            content_frame,
            text="Change Image",
            font=("Arial", 10, "bold"),
            bg="#FF9800",
            fg="white",
            padx=20,
            pady=8,
            command=self.change_image,
        )
        change_image_button.pack(pady=(0, 10))

        # Add "Add Button" button
        add_button = tk.Button(
            content_frame,
            text="Add Button",
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=8,
            command=self.add_new_button,
        )
        add_button.pack(pady=(0, 10))

        # Add save button
        save_button = tk.Button(
            content_frame,
            text="Save",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            command=lambda: self.save_data(filename),
        )
        save_button.pack()

        # Update window title
        filename_only = os.path.basename(filename)
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext == ".playmap":
            self.save_window.title(f"Controls - {filename_only}")
        elif file_ext == ".plist":
            self.save_window.title(f"Controls - {filename_only}")
        else:
            self.save_window.title(f"Controls - {filename_only}")

    def change_image(self):
        """Allow user to select and load a new image"""
        # Define image file types
        image_file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.tif"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("GIF files", "*.gif"),
            ("BMP files", "*.bmp"),
            ("TIFF files", "*.tiff *.tif"),
            ("All files", "*.*"),
        ]

        # Show file dialog to select new image
        new_image_filename = filedialog.askopenfilename(
            title="Select a new image file", 
            filetypes=image_file_types
        )

        if new_image_filename:
            try:
                # Load the new image
                self.load_image(new_image_filename)
                
                # Redraw the button models on the new image
                self.draw_button_models()
                
                # Show success message
                filename_only = os.path.basename(new_image_filename)
                messagebox.showinfo(
                    "Image Changed", 
                    f"Successfully loaded new image: {filename_only}"
                )
                
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"Failed to load new image:\n{str(e)}"
                )

    def add_new_button(self):
        """Add a new button circle to the canvas"""
        # Create key capture dialog
        key_dialog = tk.Toplevel(self.root)
        key_dialog.title("Press a Key")
        key_dialog.geometry("300x150")
        key_dialog.resizable(False, False)
        key_dialog.focus_set()
        key_dialog.grab_set()  # Make it modal

        # Center the dialog
        key_dialog.transient(self.root)

        # Variables to store the captured key
        self.captured_key = None
        self.captured_key_code = None

        # Create content frame
        dialog_frame = tk.Frame(key_dialog)
        dialog_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Instruction label
        instruction_label = tk.Label(
            dialog_frame,
            text="Press any key to assign to the new button",
            font=("Arial", 11),
            wraplength=250,
        )
        instruction_label.pack(pady=(0, 10))

        # Display label for captured key
        self.key_display_label = tk.Label(
            dialog_frame,
            text="Waiting for key press...",
            font=("Arial", 10, "bold"),
            fg="blue",
        )
        self.key_display_label.pack(pady=(0, 10))

        # Buttons frame
        button_frame = tk.Frame(dialog_frame)
        button_frame.pack()

        # OK button (initially disabled)
        self.ok_button = tk.Button(
            button_frame,
            text="OK",
            font=("Arial", 10),
            padx=20,
            pady=5,
            state="disabled",
            command=lambda: self.create_new_button_circle(key_dialog),
        )
        self.ok_button.pack(side=tk.LEFT, padx=(0, 5))

        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 10),
            padx=20,
            pady=5,
            command=key_dialog.destroy,
        )
        cancel_button.pack(side=tk.LEFT)

        # Bind key events
        key_dialog.bind("<KeyPress>", self.on_key_capture)
        key_dialog.focus_set()

    def on_key_capture(self, event):
        """Capture the pressed key"""
        self.captured_key = event.keysym

        # Convert to PlayCover keycode using our mapping
        key_name = self.captured_key
        self.captured_key_code = KeyToCode.get(key_name, event.keycode)

        # Update display
        self.key_display_label.config(
            text=f"Captured: {key_name} (Code: {self.captured_key_code})", fg="green"
        )

        # Enable OK button
        self.ok_button.config(state="normal")

    def create_new_button_circle(self, dialog):
        """Create a new button circle with the captured key"""
        if not self.captured_key or self.captured_key_code is None:
            return

        # Convert keysym to original PlayCover key name using KeyNameDiffrences
        if self.captured_key in KeyNameDifferences:
            key_name = KeyNameDifferences[self.captured_key]
        else:
            # Fallback to captured key name
            key_name = (
                self.captured_key.upper()
                if len(self.captured_key) == 1
                else self.captured_key
            )

        # Create new button data with PlayCover-compatible keycode
        new_button = {
            "keyCode": self.captured_key_code,
            "keyName": key_name,
            "transform": {"size": 5.0, "xCoord": 0.5, "yCoord": 0.5},
        }

        # Add to buttonModels
        if "buttonModels" not in self.plist_data:
            self.plist_data["buttonModels"] = []

        self.plist_data["buttonModels"].append(new_button)

        # Redraw all circles to include the new one
        self.draw_button_models()

        # Close dialog
        dialog.destroy()

        # Show success message
        # messagebox.showinfo(
        #     "Button Added",
        #     f"New button '{new_button['keyName']}' (Code: {new_button['keyCode']}) added at center.\nYou can drag it to the desired position."
        # )

    def save_data(self, original_filename):
        """Save the updated data to a file"""
        # Get the file extension to determine save format
        file_ext = os.path.splitext(original_filename)[1].lower()

        # Set up file dialog based on original file type
        if file_ext in [".plist", ".playmap"]:
            file_types = [
                ("Playmap files", "*.playmap"),
                ("Plist files", "*.plist"),
                ("All files", "*.*"),
            ]
            default_ext = file_ext
        else:
            file_types = [("JSON files", "*.json"), ("All files", "*.*")]
            default_ext = ".json"

        # Show save dialog
        save_filename = filedialog.asksaveasfilename(
            title="Save updated button positions",
            defaultextension=default_ext,
            filetypes=file_types,
            initialfile=os.path.basename(original_filename),
        )

        if save_filename:
            try:
                save_ext = os.path.splitext(save_filename)[1].lower()

                if save_ext in [".plist", ".playmap"]:
                    # Save as plist
                    with open(save_filename, "wb") as plist_file:
                        plistlib.dump(self.plist_data, plist_file)
                else:
                    # Save as JSON
                    with open(save_filename, "w", encoding="utf-8") as json_file:
                        json.dump(self.plist_data, json_file, indent=2, default=str)

                messagebox.showinfo(
                    "Success", f"File saved successfully to:\n{save_filename}"
                )

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def load_plist(self, filename):
        """Load and parse a plist file"""
        try:
            with open(filename, "rb") as plist_file:
                self.plist_data = plistlib.load(plist_file)

            # Create save window instead of data viewer
            self.create_save_window(filename)
            self.plist_name = filename
            return self.plist_data

        except Exception as e:
            raise Exception(f"Failed to parse plist file: {str(e)}")

    def load_json(self, filename):
        """Load and parse a JSON file"""
        try:
            with open(filename, "r", encoding="utf-8") as json_file:
                self.plist_data = json.load(json_file)

            # Create save window instead of data viewer
            self.create_save_window(filename)

            return self.plist_data

        except Exception as e:
            raise Exception(f"Failed to parse JSON file: {str(e)}")

    def on_double_click(self, event):
        """Handle double-click events to open button edit popup"""
        # Find the closest item to the click
        item = self.canvas.find_closest(event.x, event.y)[0]

        # Get tags safely
        tags = self.canvas.gettags(item)

        # Check if it's a button circle or text
        if item in self.button_circles or (
            tags and tags[0] in ["button_circle", "button_text"]
        ):
            # If it's text, find the corresponding circle
            if tags and tags[0] == "button_text":
                # Find the circle that corresponds to this text
                for circle_id, data in self.button_circles.items():
                    if data["text_id"] == item:
                        item = circle_id
                        break

            if item in self.button_circles:
                self.open_button_edit_popup(item)

    def open_button_edit_popup(self, circle_id):
        """Open a popup with options to edit the button"""
        circle_data = self.button_circles[circle_id]
        button_index = circle_data["button_index"]
        button_data = circle_data["button_data"]

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Edit Button")
        popup.geometry("300x200")
        popup.resizable(False, False)
        popup.grab_set()  # Make it modal
        popup.transient(self.root)

        # Center the popup
        popup.focus_set()

        # Create main frame
        main_frame = tk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Current button info
        info_label = tk.Label(
            main_frame,
            text=f"Editing: {button_data.get('keyName', 'Unknown')}",
            font=("Arial", 12, "bold"),
            fg="blue",
        )
        info_label.pack(pady=(0, 15))

        # Button 1: Manual Key Name
        manual_key_button = tk.Button(
            main_frame,
            text="Manual Key Name",
            font=("Arial", 10, "bold"),
            bg="#FF9800",
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self.manual_key_name(popup, circle_id),
        )
        manual_key_button.pack(pady=3, fill=tk.X)

        # Button 2: Capture Key
        capture_key_button = tk.Button(
            main_frame,
            text="Capture Key",
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self.capture_key_for_button(popup, circle_id),
        )
        capture_key_button.pack(pady=3, fill=tk.X)

        # Button 3: Change Size
        change_size_button = tk.Button(
            main_frame,
            text="Change Size",
            font=("Arial", 10, "bold"),
            bg="#9C27B0",
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self.change_button_size(popup, circle_id),
        )
        change_size_button.pack(pady=3, fill=tk.X)

        # Close button
        close_button = tk.Button(
            main_frame,
            text="Close",
            font=("Arial", 10),
            bg="#666666",
            fg="white",
            padx=20,
            pady=5,
            command=popup.destroy,
        )
        close_button.pack(pady=(15, 0))

    def manual_key_name(self, parent_popup, circle_id):
        """Open dialog to manually enter key name"""
        parent_popup.destroy()

        circle_data = self.button_circles[circle_id]
        button_index = circle_data["button_index"]
        current_key_name = circle_data["button_data"].get("keyName", "")

        # Create input dialog
        input_dialog = tk.Toplevel(self.root)
        input_dialog.title("Manual Key Name")
        input_dialog.geometry("300x150")
        input_dialog.resizable(False, False)
        input_dialog.grab_set()
        input_dialog.transient(self.root)
        input_dialog.focus_set()

        # Create frame
        dialog_frame = tk.Frame(input_dialog)
        dialog_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Instruction label
        instruction_label = tk.Label(
            dialog_frame, text="Enter the key name:", font=("Arial", 11)
        )
        instruction_label.pack(pady=(0, 10))

        # Entry field
        key_entry = tk.Entry(dialog_frame, font=("Arial", 12), width=20)
        key_entry.pack(pady=(0, 15))
        key_entry.insert(0, current_key_name)
        key_entry.select_range(0, tk.END)
        key_entry.focus_set()

        # Buttons frame
        button_frame = tk.Frame(dialog_frame)
        button_frame.pack()

        def save_manual_key():
            new_key_name = key_entry.get().strip()
            if new_key_name:
                # Update the button data
                self.plist_data["buttonModels"][button_index]["keyName"] = new_key_name
                # Redraw to show the change
                self.draw_button_models()
                input_dialog.destroy()

        # Save button
        save_button = tk.Button(
            button_frame,
            text="Save",
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            command=save_manual_key,
        )
        save_button.pack(side=tk.LEFT, padx=(0, 5))

        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 10),
            padx=20,
            pady=5,
            command=input_dialog.destroy,
        )
        cancel_button.pack(side=tk.LEFT)

        # Bind Enter key to save
        key_entry.bind("<Return>", lambda e: save_manual_key())

    def capture_key_for_button(self, parent_popup, circle_id):
        """Open dialog to capture a new key for existing button"""
        parent_popup.destroy()

        circle_data = self.button_circles[circle_id]
        button_index = circle_data["button_index"]

        # Create key capture dialog (similar to add_new_button but for editing)
        key_dialog = tk.Toplevel(self.root)
        key_dialog.title("Capture New Key")
        key_dialog.geometry("300x150")
        key_dialog.resizable(False, False)
        key_dialog.focus_set()
        key_dialog.grab_set()
        key_dialog.transient(self.root)

        # Variables to store the captured key
        self.captured_key = None
        self.captured_key_code = None

        # Create content frame
        dialog_frame = tk.Frame(key_dialog)
        dialog_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Instruction label
        instruction_label = tk.Label(
            dialog_frame,
            text="Press any key to assign to this button",
            font=("Arial", 11),
            wraplength=250,
        )
        instruction_label.pack(pady=(0, 10))

        # Display label for captured key
        self.key_display_label = tk.Label(
            dialog_frame,
            text="Waiting for key press...",
            font=("Arial", 10, "bold"),
            fg="blue",
        )
        self.key_display_label.pack(pady=(0, 10))

        # Buttons frame
        button_frame = tk.Frame(dialog_frame)
        button_frame.pack()

        def update_button_key():
            if self.captured_key and self.captured_key_code is not None:
                # Convert keysym to PlayCover key name
                if self.captured_key in KeyNameDifferences:
                    key_name = KeyNameDifferences[self.captured_key]
                else:
                    key_name = (
                        self.captured_key.upper()
                        if len(self.captured_key) == 1
                        else self.captured_key
                    )

                # Update the button data
                self.plist_data["buttonModels"][button_index][
                    "keyCode"
                ] = self.captured_key_code
                self.plist_data["buttonModels"][button_index]["keyName"] = key_name

                # Redraw to show the change
                self.draw_button_models()
                key_dialog.destroy()

        # OK button (initially disabled)
        self.ok_button = tk.Button(
            button_frame,
            text="OK",
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            state="disabled",
            command=update_button_key,
        )
        self.ok_button.pack(side=tk.LEFT, padx=(0, 5))

        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 10),
            padx=20,
            pady=5,
            command=key_dialog.destroy,
        )
        cancel_button.pack(side=tk.LEFT)

        # Bind key events
        key_dialog.bind("<KeyPress>", self.on_key_capture)
        key_dialog.focus_set()

    def change_button_size(self, parent_popup, circle_id):
        """Open dialog to change button size"""
        parent_popup.destroy()

        circle_data = self.button_circles[circle_id]
        button_index = circle_data["button_index"]
        current_size = circle_data["button_data"]["transform"].get("size", 5.0)

        # Create size input dialog
        size_dialog = tk.Toplevel(self.root)
        size_dialog.title("Change Button Size")
        size_dialog.geometry("300x150")
        size_dialog.resizable(False, False)
        size_dialog.grab_set()
        size_dialog.transient(self.root)
        size_dialog.focus_set()

        # Create frame
        dialog_frame = tk.Frame(size_dialog)
        dialog_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Instruction label
        instruction_label = tk.Label(
            dialog_frame, text="Enter button size (1-20):", font=("Arial", 11)
        )
        instruction_label.pack(pady=(0, 10))

        # Entry field
        size_entry = tk.Entry(dialog_frame, font=("Arial", 12), width=10)
        size_entry.pack(pady=(0, 15))
        size_entry.insert(0, str(current_size))
        size_entry.select_range(0, tk.END)
        size_entry.focus_set()

        # Buttons frame
        button_frame = tk.Frame(dialog_frame)
        button_frame.pack()

        def save_size():
            try:
                new_size = float(size_entry.get().strip())
                if 1 <= new_size <= 20:
                    # Update the button data
                    self.plist_data["buttonModels"][button_index]["transform"][
                        "size"
                    ] = new_size
                    # Redraw to show the change
                    self.draw_button_models()
                    size_dialog.destroy()
                else:
                    messagebox.showwarning(
                        "Invalid Size", "Size must be between 1 and 20"
                    )
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number")

        # Save button
        save_button = tk.Button(
            button_frame,
            text="Save",
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            command=save_size,
        )
        save_button.pack(side=tk.LEFT, padx=(0, 5))

        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 10),
            padx=20,
            pady=5,
            command=size_dialog.destroy,
        )
        cancel_button.pack(side=tk.LEFT)

        # Bind Enter key to save
        size_entry.bind("<Return>", lambda e: save_size())


def main():
    # Use TkinterDnD for drag-and-drop support
    root = TkinterDnD.Tk()
    app = ImageViewer(root)

    # Hide the window initially
    root.withdraw()

    # First popup: Select an image file
    image_file_types = [
        ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.tif"),
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg *.jpeg"),
        ("GIF files", "*.gif"),
        ("BMP files", "*.bmp"),
        ("TIFF files", "*.tiff *.tif"),
        ("All files", "*.*"),
    ]

    image_filename = filedialog.askopenfilename(
        title="First: Select an image file to view", filetypes=image_file_types
    )

    if not image_filename:
        # User cancelled image selection, exit
        root.quit()
        return

    # Second popup: Select a plist or JSON file
    data_file_types = [
        ("Data files", "*.plist *.json *.playmap"),
        ("Plist files", "*.plist"),
        ("JSON files", "*.json"),
        ("Playmap files", "*.playmap"),
        ("All files", "*.*"),
    ]

    data_filename = filedialog.askopenfilename(
        title="Second: Select a plist, JSON, or playmap file to view",
        filetypes=data_file_types,
    )

    if not data_filename:
        # User cancelled data file selection, exit
        root.quit()
        return

    # Enable drag-and-drop on the main window
    def on_drop(event):
        dropped_file = event.data.strip("{}")  # Remove curly braces if present
        # Close the old controls window if it exists
        if hasattr(app, 'save_window') and app.save_window is not None:
            try:
                app.save_window.destroy()
            except Exception:
                pass
            app.save_window = None
        if is_image_file(dropped_file):
            try:
                app.load_image(dropped_file)
                app.draw_button_models()
                app.create_save_window(app.plist_name)
                messagebox.showinfo("Image Loaded", f"Loaded image: {os.path.basename(dropped_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
        elif is_plist_file(dropped_file):
            try:
                app.load_plist(dropped_file)
                app.draw_button_models()
                messagebox.showinfo("Plist Loaded", f"Loaded plist/playmap: {os.path.basename(dropped_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load plist/playmap:\n{str(e)}")
        else:
            messagebox.showwarning("Unsupported File", "File type not supported for drag-and-drop.")

    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    # Show the window and load both files
    root.deiconify()

    try:
        # Load and display the image first
        app.load_image(image_filename)

        # Load and display the data file in a separate window
        file_ext = os.path.splitext(data_filename)[1].lower()

        if file_ext in [".plist", ".playmap"]:
            data = app.load_plist(data_filename)
        elif file_ext == ".json":
            data = app.load_json(data_filename)
        else:
            # Try to load as JSON first, then plist if that fails
            try:
                data = app.load_json(data_filename)
            except:
                data = app.load_plist(data_filename)

        # Draw button models on the image canvas
        app.draw_button_models()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load files:\n{str(e)}")
        root.quit()
        return

    root.mainloop()


if __name__ == "__main__":
    main()
