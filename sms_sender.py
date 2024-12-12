import tkinter as tk
from tkinter import ttk, messagebox
from twilio.rest import Client
import os
import json
from dotenv import load_dotenv

class SMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SMS Sender")
        
        # Load environment variables and setup
        load_dotenv()
        
        # Twilio setup
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Check Twilio credentials
        if not all([self.account_sid, self.auth_token, self.from_number]):
            messagebox.showerror("Error", "Missing Twilio credentials")
            root.quit()
        
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            messagebox.showerror("Twilio Error", f"Failed to initialize: {str(e)}")
            root.quit()
        
        # Number mapping file
        self.NUMBER_MAP_FILE = 'number_mapping.json'
        self.number_mapping = self.load_number_mapping()
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')
        
        # Create tabs
        self.create_send_tab()
        self.create_link_tab()
        
        # Set window size and center
        self.set_window_geometry(400, 300)
    
    def load_number_mapping(self):
        """Load number mapping from JSON file"""
        try:
            with open(self.NUMBER_MAP_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_number_mapping(self):
        """Save number mapping to JSON file"""
        with open(self.NUMBER_MAP_FILE, 'w') as f:
            json.dump(self.number_mapping, f, indent=4)
    
    def create_send_tab(self):
        """Create the Send SMS tab"""
        send_frame = ttk.Frame(self.notebook)
        self.notebook.add(send_frame, text="Send SMS")
        
        # Short number input
        ttk.Label(send_frame, text="Enter Short Number:").pack(pady=10)
        self.short_number_entry = ttk.Entry(send_frame, width=20)
        self.short_number_entry.pack(pady=5)
        
        # Message input
        ttk.Label(send_frame, text="Message:").pack(pady=5)
        self.message_entry = tk.Text(send_frame, height=3, width=40)
        self.message_entry.pack(pady=5)
        
        # Send button
        send_button = ttk.Button(send_frame, text="Send SMS", command=self.send_sms)
        send_button.pack(pady=10)
        
        # Existing Mappings Display
        ttk.Label(send_frame, text="Existing Mappings:").pack(pady=5)
        self.mappings_text = tk.Text(send_frame, height=5, width=40)
        self.mappings_text.pack(pady=5)
        self.update_mappings_display()
    
    def create_link_tab(self):
        """Create the Link Numbers tab"""
        link_frame = ttk.Frame(self.notebook)
        self.notebook.add(link_frame, text="Link Numbers")
        
        # Short Number Input
        ttk.Label(link_frame, text="Short Number (10 digits):").pack(pady=5)
        self.link_short_number_entry = ttk.Entry(link_frame, width=20)
        self.link_short_number_entry.pack(pady=5)
        
        # Phone Number Input
        ttk.Label(link_frame, text="Full Phone Number (with +1):").pack(pady=5)
        self.full_phone_entry = ttk.Entry(link_frame, width=20)
        self.full_phone_entry.pack(pady=5)
        self.full_phone_entry.insert(0, '+1')
        
        # Link button
        link_button = ttk.Button(link_frame, text="Link Numbers", command=self.link_numbers)
        link_button.pack(pady=10)
    
    def link_numbers(self):
        """Link a short number to a full phone number"""
        short_number = self.link_short_number_entry.get().strip()
        full_phone = self.full_phone_entry.get().strip()
        
        # Validate short number (10 digits)
        if not (short_number.isdigit() and len(short_number) == 10):
            messagebox.showerror("Error", "Short number must be 10 digits")
            return
        
        # Validate full phone number
        if not (full_phone.startswith('+1') and len(full_phone) == 12):
            messagebox.showerror("Error", "Phone number must be in +1XXXXXXXXXX format")
            return
        
        # Store mapping
        self.number_mapping[short_number] = full_phone
        self.save_number_mapping()
        
        # Update UI
        self.update_mappings_display()
        messagebox.showinfo("Success", "Number linked successfully!")
        
        # Clear entries
        self.link_short_number_entry.delete(0, tk.END)
        self.full_phone_entry.delete(0, tk.END)
        self.full_phone_entry.insert(0, '+1')
    
    def send_sms(self):
        """Send SMS to the linked phone number"""
        short_number = self.short_number_entry.get().strip()
        message = self.message_entry.get("1.0", tk.END).strip()
        
        # Debug prints
        print(f"Short Number: {short_number}")
        print(f"Message: {message}")
        print(f"Number Mapping: {self.number_mapping}")
        
        # Validate short number input
        if not (short_number.isdigit() and len(short_number) == 10):
            messagebox.showerror("Error", "Short number must be 10 digits")
            return
        
        # Validate message
        if not message:
            messagebox.showerror("Error", "Message cannot be empty")
            return
        
        # Get full phone number
        full_phone = self.number_mapping.get(short_number)
        print(f"Full Phone Number Found: {full_phone}")
        
        if not full_phone:
            messagebox.showerror("Error", f"No phone number linked to {short_number}")
            return
        
        try:
            # Send message via Twilio
            print("Attempting to send message...")
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=full_phone
            )
            print(f"Message SID: {message_obj.sid}")
            messagebox.showinfo("Success", f"Message sent to {full_phone}")
            
            # Clear message entry
            self.message_entry.delete("1.0", tk.END)
        except Exception as e:
            print(f"Send Error: {e}")
            messagebox.showerror("Send Error", str(e))

    
    def update_mappings_display(self):
        """Update the display of existing number mappings"""
        # Clear existing text
        self.mappings_text.config(state=tk.NORMAL)
        self.mappings_text.delete("1.0", tk.END)
        
        # Display mappings
        for short, full in self.number_mapping.items():
            self.mappings_text.insert(tk.END, f"{short}: {full}\n")
        
        self.mappings_text.config(state=tk.DISABLED)
    
    def set_window_geometry(self, width, height):
        """Center the window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

def main():
    root = tk.Tk()
    app = SMSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()