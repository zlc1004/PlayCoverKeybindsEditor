# PlayCoverKeybindsEditor

This is a simple keybinds/keymap editor for PlayCover, a tool to run iOS apps on macOS.

## Features

- Load and display images
- Edit keybinds visually
- Save changes to keymap files

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/zlc1004/PlayCoverKeybindsEditor.git
   # or github cli
   gh repo clone zlc1004/PlayCoverKeybindsEditor

   cd PlayCoverKeybindsEditor
   ```
2. Install dependencies with conda:
   ```bash
   conda env create -f environment.yml -p ./.conda
   conda activate ./.conda
   ```
3. Run the application:
   ```bash
   python main.py
   ```