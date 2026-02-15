import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

window = ctk.CTk()
window.title("Jarvis AI Assistant")
window.minsize(1000, 1000)
window.configure(padx=40, pady=40)

# Header Frame
header_frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=15)
header_frame.pack(pady=20, fill="x")

# Bot Avatar
avatar_label = ctk.CTkLabel(header_frame, text="🤖", font=("Arial", 50))
avatar_label.pack(pady=(30, 10))

# Title
chatbot_label = ctk.CTkLabel(
    header_frame,
    text="Jarvis Bot",
    font=("Arial Bold", 42),
    text_color="#3b8ed0"
)
chatbot_label.pack(pady=15)

# Greeting
chat_bot_greetings = ctk.CTkLabel(
    header_frame,
    text="My name is Jarvis bot, how may I help you?",
    font=("Arial", 18),
    text_color="#a0a0a0"
)
chat_bot_greetings.pack(pady=(5, 30))

# Input Frame
input_frame = ctk.CTkFrame(window, fg_color="transparent")
input_frame.pack(pady=30, fill="x")

# Input Field
chatbot_input = ctk.CTkEntry(
    input_frame,
    width=600,
    height=60,
    font=("Arial", 16),
    placeholder_text="Type your message here...",
    corner_radius=10,
    border_width=2
)
chatbot_input.pack(pady=20)

# Send Button
send_button = ctk.CTkButton(
    input_frame,
    text="Send Message",
    width=200,
    height=50,
    font=("Arial Bold", 16),
    corner_radius=10
)
send_button.pack(pady=10)

# Footer
footer_label = ctk.CTkLabel(
    window,
    text="Powered by AI Technology",
    font=("Arial", 11),
    text_color="#5a5a5a"
)
footer_label.pack(side="bottom", pady=20)

window.mainloop()