import tkinter as tk
from tkinter import messagebox
from twilio.rest import Client
import os
from dotenv import load_dotenv

def send_sms():
    # Get the phone number from the entry field
    phone_number = phone_entry.get().strip()
    
    # Basic validation
    if not phone_number:
        messagebox.showerror("Error", "Please enter a phone number")
        return
        
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    try:
        # Send the message using Twilio
        message = client.messages.create(
            body=preset_message,
            from_=from_number,
            to=phone_number
        )
        messagebox.showinfo("Success", "Message sent successfully!")
        phone_entry.delete(0, tk.END)  # Clear the entry
        phone_entry.insert(0, "+1")    # Reset to default country code
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send message: {str(e)}")

# Load environment variables from .env file
load_dotenv()

# Get Twilio credentials from environment variables
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('TWILIO_PHONE_NUMBER')
preset_message = os.getenv('PRESET_MESSAGE', 'Default preset message')

# Check if credentials are available
if not all([account_sid, auth_token, from_number]):
    print("Error: Missing Twilio credentials in .env file")
    exit(1)

# Initialize Twilio client
try:
    client = Client(account_sid, auth_token)
except Exception as e:
    print(f"Error initializing Twilio client: {str(e)}")
    exit(1)

# Create main window
root = tk.Tk()
root.title("SMS Sender")

# Create and pack widgets
# Phone number input
tk.Label(root, text="Enter Phone Number:").pack(pady=10)
phone_entry = tk.Entry(root, width=20)
phone_entry.pack(pady=5)
phone_entry.insert(0, "+1")  # Default country code for US

# Message preview
tk.Label(root, text="Message Preview:").pack(pady=10)
message_preview = tk.Text(root, height=3, width=40)
message_preview.pack(pady=5)
message_preview.insert(tk.END, preset_message)
message_preview.config(state='disabled')  # Make it read-only

# Send button
tk.Button(root, text="Send SMS", command=send_sms).pack(pady=20)

# Center window
window_width = 400
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width/2) - (window_width/2)
y = (screen_height/2) - (window_height/2)
root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')

# Start the application
if __name__ == "__main__":
    root.mainloop()