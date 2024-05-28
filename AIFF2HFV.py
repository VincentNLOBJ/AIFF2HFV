import machfs
import os
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import io

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def truncate_filename(filename, max_length):
    # Remove extension
    name, ext = os.path.splitext(filename)
    # Truncate name if it's longer than max_length
    truncated_name = name[:max_length]
    # Return the truncated name with the original extension
    return truncated_name + ext

def transfer_file_to_hfv(hfv_path, source_file_paths, volume_name='AIFF'):
    try:
        # Verify the HFV file exists and is not empty
        if not os.path.isfile(hfv_path) or os.path.getsize(hfv_path) == 0:
            messagebox.showerror("Error", f"'{hfv_path}' not found or empty")
            print(f"Error: HFV file '{hfv_path}' does not exist or is empty.")
            return

        # Open the HFV file and read its content
        with open(hfv_path, 'rb') as hfv_file:
            flat = hfv_file.read()

        volume = machfs.Volume()
        volume.read(flat)
        volume.name = volume_name

        for source_file_path in source_file_paths:
            try:
                with open(source_file_path, 'rb') as source_file:
                    file_data = source_file.read()

                # Get the file name from the source file path and truncate if necessary
                file_name = os.path.basename(source_file_path)
                file_name = truncate_filename(file_name, 26)

                # Create a new file in the root directory of the volume
                new_file = machfs.File()
                new_file.data = file_data
                new_file.type = b'AIFF'
                new_file.creator = b'????'

                # Add the new file to the root directory
                volume[file_name] = new_file
            except Exception as e:
                print(f"Error reading or processing file '{source_file_path}': {e}")
                return

        # Write the modified volume to a buffer
        buffer = io.BytesIO()
        buffer.write(volume.write(
            size=len(flat),  
            align=512,       
            desktopdb=True,  
            bootable=True   
        ))
        buffer.seek(0)  

        # Write the buffer content back to the HFV file
        with open(hfv_path, 'wb') as hfv_file:
            hfv_file.write(buffer.read())
        messagebox.showinfo("Import Complete", "Files have been imported successfully.")


    except Exception as e:
        messagebox.showerror("Error", f"Error during HFV transfer process: {e}")

def select_files_and_transfer():
    root = tk.Tk()
    root.withdraw()
    root.iconbitmap(resource_path('naomi9.ico'))

    # Open file dialog
    source_file_paths = filedialog.askopenfilenames(
        title="Select AIFF Files",
        filetypes=[("AIFF Files", "*.aiff"), ("All Files", "*.*")]
    )

    if not source_file_paths:
        print("No files selected.")
        return

    # Path to the HFV file
    hfv_path = "AIFF_HDD.hfv"

    # Transfer the selected files to the HFV volume
    transfer_file_to_hfv(hfv_path, source_file_paths)

select_files_and_transfer()
