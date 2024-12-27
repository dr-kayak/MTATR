import random
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog  
import csv
import os

# File path for technicians CSV
CSV_FILE_PATH = 


# List to store technician data
technicians = []

# Initialize prev_selected_technician
prev_selected_technician = None

# Function to load technicians from CSV
def load_technicians():
    global technicians
    technicians.clear()  # Clear the list before loading
    try:
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                
                # Check if CSV headers are correct
                if reader.fieldnames != ['name', 'ticket_load', 'max_ticket_load']:
                    messagebox.showerror("Error", "CSV file headers do not match expected format.")
                    return

                technicians = [
                    {
                        'name': row['name'],
                        'ticket_load': int(row['ticket_load']),
                        'max_ticket_load': int(row['max_ticket_load']),
                    }
                    for row in reader
                ]
                if not technicians:
                    messagebox.showinfo("Info", "No technicians found in the CSV file.")
        else:
            messagebox.showerror("Error", f"Technicians file not found at {CSV_FILE_PATH}!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading technicians: {e}")



# Function to save technicians to CSV
def save_technicians():
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        fieldnames = ['name', 'ticket_load', 'max_ticket_load']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for tech in technicians:
            # Create a copy of the technician dictionary excluding the 'weight' field
            tech_to_save = {key: tech[key] for key in fieldnames}
            writer.writerow(tech_to_save)



# Function to calculate weighting factor
def calculate_weighting_factor(ticket_load):
    return max(1 - ticket_load / 100, 0)

# Function to assign ticket
def assign_ticket():
    global prev_selected_technician

    # Load technicians from CSV to get the latest data
    load_technicians()

    # Exclude technicians with a ticket load over their max limit
    available_technicians = [tech for tech in technicians if tech['ticket_load'] < tech['max_ticket_load']]

    if not available_technicians:
        log.insert(tk.END, "All technicians have exceeded their maximum ticket load. Unable to assign a ticket.\n")
        return

    selected_technician = None

    if prev_selected_technician:
        available_technicians = [tech for tech in available_technicians if tech['name'] != prev_selected_technician['name']]

    for tech in available_technicians:
        tech['weight'] = calculate_weighting_factor(tech['ticket_load'])

    total_weight = sum(tech['weight'] for tech in available_technicians)
    rand_num = random.uniform(0, total_weight)

    cumulative_weight = 0
    for tech in available_technicians:
        cumulative_weight += tech['weight']
        if rand_num <= cumulative_weight:
            selected_technician = tech
            break

    if selected_technician:
        result_message = f"Ticket assigned to {selected_technician['name']}."
        log.insert(tk.END, result_message + "\n")

        selected_technician['ticket_load'] += 1
        prev_selected_technician = selected_technician

        for i, tech in enumerate(technicians):
            if tech['name'] == selected_technician['name']:
                entry_fields[i].delete(0, tk.END)
                entry_fields[i].insert(0, str(tech['ticket_load']))
                break

        # Save changes to CSV after updating the ticket load
        save_technicians()



# Function to show technicians and edit their ticket load
def show_technicians():
    tech_window = tk.Toplevel(window)
    tech_window.title("Technicians")
    tech_window.geometry("500x400")  # Adjusted height for additional buttons

    def update_max_ticket_load(tech_index, entry_field):
        try:
            new_max_load = int(entry_field.get())
            technicians[tech_index]['max_ticket_load'] = new_max_load
            messagebox.showinfo("Success", f"Max ticket load for '{technicians[tech_index]['name']}' updated to {new_max_load}.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter a valid number.")

    def add_tech():
        name = tk.simpledialog.askstring("Add Technician", "Enter Technician's Name:")
        if not name:
            return  # No name entered
        
        try:
            max_load = int(tk.simpledialog.askstring("Add Technician", "Enter Default Max Load:"))
            technicians.append({'name': name, 'ticket_load': 0, 'max_ticket_load': max_load})
            log.insert(tk.END, f"Added Technician: {name} with Max Load: {max_load}\n")
            show_technicians()  # Refresh the technician list
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input! Please enter a valid number for max load.")

    def remove_tech():
        tech_names = [tech['name'] for tech in technicians]
        if not tech_names:
            messagebox.showinfo("Info", "No technicians to remove.")
            return
        
        selected_tech = tk.simpledialog.askstring("Remove Technician", "Select Technician to Remove:\n" + "\n".join(tech_names))
        if selected_tech and selected_tech in tech_names:
            technicians[:] = [tech for tech in technicians if tech['name'] != selected_tech]
            log.insert(tk.END, f"Removed Technician: {selected_tech}\n")
            show_technicians()  # Refresh the technician list
        else:
            messagebox.showerror("Error", "Technician not found!")

    for i, tech in enumerate(technicians):
        tk.Label(tech_window, text=f"{tech['name']} - Ticket Load: {tech['ticket_load']} / Max: {tech['max_ticket_load']}").grid(row=i, column=0, padx=10, pady=5, sticky="w")

        max_load_entry = tk.Entry(tech_window)
        max_load_entry.insert(0, str(tech['max_ticket_load']))
        max_load_entry.grid(row=i, column=1, padx=10, pady=5)

        update_button = tk.Button(tech_window, text="Update Load", command=lambda i=i, entry=max_load_entry: update_max_ticket_load(i, entry))
        update_button.grid(row=i, column=3, padx=10, pady=5)

    # Add Add Tech and Remove Tech buttons
    add_button = tk.Button(tech_window, text="Add Tech", command=add_tech)
    add_button.grid(row=len(technicians), column=0, padx=10, pady=(10, 5), sticky="ew")

    remove_button = tk.Button(tech_window, text="Remove Tech", command=remove_tech)
    remove_button.grid(row=len(technicians), column=1, padx=10, pady=(10, 5), sticky="ew")

    # Adjust grid weights to ensure proper resizing
    tech_window.grid_columnconfigure(0, weight=1)
    tech_window.grid_columnconfigure(1, weight=1)
    tech_window.grid_columnconfigure(2, weight=0)
    tech_window.grid_columnconfigure(3, weight=0)



# Function to display information about the application
def display_about_info():
    about_info = """
    Malachi's Totally Awesome Ticket Randomizer
    Version 1.2
    Developed by Malachi McRee
    This application randomly assigns tickets to technicians 
    based on their workload.
    
    **v1.2
        -General bug fixes
        -Added .csv that allows for easier updating of techs as 
        well as persistant storage of data.
        -Added function to alter technician maximum load
        -Reformatted "About" menu.
        -Removed Herobrine

    **v1.1.2
        -General bug fixes

    **v1.0
        -Inital release
    """
    messagebox.showinfo("About", about_info)

# Function to add a menu for debug options
def add_debug_menu():
    debug_menu = tk.Menu(options_menu)
    options_menu.add_cascade(label="Debug", menu=debug_menu)
    debug_menu.add_command(label="Test Weight", command=test_weight)
    debug_menu.add_command(label="Show Current Weight", command=show_current_weight)

# Function for testing weight
def test_weight():
    selections_count = {tech['name']: 0 for tech in technicians}

    for _ in range(1000):
        available_technicians = [tech for tech in technicians if tech['ticket_load'] < tech['max_ticket_load']]

        if not available_technicians:
            continue

        for tech in available_technicians:
            tech['weight'] = calculate_weighting_factor(tech['ticket_load'])

        total_weight = sum(tech['weight'] for tech in available_technicians)
        rand_num = random.uniform(0, total_weight)

        cumulative_weight = 0
        for tech in available_technicians:
            cumulative_weight += tech['weight']
            if rand_num <= cumulative_weight:
                selected_technician = tech
                break

        selections_count[selected_technician['name']] += 1

    log.insert(tk.END, "Test Weight Results (1000 Selections):\n")
    for tech, count in selections_count.items():
        log.insert(tk.END, f"{tech}: {count}\n")

# Function to show current weight
def show_current_weight():
    log.insert(tk.END, "Current Weights:\n")
    for tech in technicians:
        weight = calculate_weighting_factor(tech['ticket_load'])
        log.insert(tk.END, f"{tech['name']}: {weight}\n")

# Function to update ticket load when entry field loses focus
def update_ticket_load(event, tech_index):
    try:
        new_load = int(entry_fields[tech_index].get())
        technicians[tech_index]['ticket_load'] = new_load
        save_technicians()  # Save changes to CSV
    except ValueError:
        messagebox.showerror("Error", "Invalid input! Please enter a valid number.")
        entry_fields[tech_index].delete(0, tk.END)
        entry_fields[tech_index].insert(0, str(technicians[tech_index]['ticket_load']))

# Create a Tkinter window
window = tk.Tk()
window.title("Malachi's Totally Awesome Ticket Randomizer")
window.geometry("425x425")  # Set window size
window.configure(bg="#2B2B2B")  # Set background color to dark gray

# Load technicians from the CSV
load_technicians()

# Create labels and entry fields for each technician
# Create labels and entry fields for each technician
entry_fields = []
for i, tech in enumerate(technicians):
    tk.Label(window, text=f"{tech['name']}", bg="#2B2B2B", fg="#FFFFFF").grid(row=i, column=0, padx=10, pady=5, sticky="w")  # Changed from "e" to "w"
    entry = tk.Entry(window, bg="#FFFFFF", fg="#2B2B2B")
    entry.insert(0, str(tech['ticket_load']))
    entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
    entry.bind("<FocusOut>", lambda event, tech_index=i: update_ticket_load(event, tech_index))
    entry_fields.append(entry)


# Create a button to assign the ticket
assign_button = tk.Button(window, text="Assign Ticket", command=assign_ticket, bg="#007ACC", fg="#FFFFFF", relief=tk.FLAT)
assign_button.grid(row=len(technicians), column=0, columnspan=2, padx=10, pady=10, sticky="ew")

# Create a menu
menu = tk.Menu(window)
window.config(menu=menu)
options_menu = tk.Menu(menu)
menu.add_cascade(label="Options", menu=options_menu)
options_menu.add_command(label="Technicians", command=show_technicians)
options_menu.add_separator()
options_menu.add_command(label="About", command=display_about_info)  # About menu option

# Add debug menu
add_debug_menu()

# Create a scrollable log area
log = scrolledtext.ScrolledText(window, width=35, height=15, bg="#FFFFFF", fg="#2B2B2B")
log.grid(row=len(technicians) + 1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")

# Center all widgets within the window
for i in range(len(technicians) + 2):
    window.grid_rowconfigure(i, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)

# Run the Tkinter event loop
window.mainloop()
