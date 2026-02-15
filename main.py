import customtkinter as ctk
import http.client
import json
import socket
import time
import threading

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Create main window
window = ctk.CTk()
window.title("Jarvis AI Assistant")
window.minsize(1000, 1000)
window.configure(padx=40, pady=40)

# Status label (for showing AI thinking status)
status_label = None
response_text = None

#Setting the backend

#settinf the theme
def toggle_theme():
    """Toggle theme between dark and light"""
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("light")
        theme_button.configure(text="🌙 Dark Mode")
        # Change frames to light colors
        header_frame.configure(fg_color="#f0f0f0")
        response_frame.configure(fg_color="#f0f0f0")
        response_text.configure(fg_color="#ffffff")
    else:
        ctk.set_appearance_mode("dark")
        theme_button.configure(text="☀️ Light Mode")
        # Change frames back to dark colors
        header_frame.configure(fg_color="#1a1a1a")
        response_frame.configure(fg_color="#1a1a1a")
        response_text.configure(fg_color="#0a0a0a")

#Setting the API and responding the users mesage
def update_status(message):
    """Update status label with current AI activity"""
    global status_label
    if status_label:
        status_label.configure(text=message)


def clear_waiting_message():
    """Clear the waiting/loading message"""
    global status_label
    if status_label:
        status_label.configure(text="")


def update_ui_with_token(response):
    """Display AI response in the UI"""
    global response_text
    if response_text:
        # Enable editing temporarily
        response_text.configure(state="normal")
        response_text.delete("1.0", "end")
        response_text.insert("1.0", response)
        response_text.configure(state="disabled")


def show_error(error_message):
    """Show error message to user"""
    global response_text
    if response_text:
        response_text.configure(state="normal")
        response_text.delete("1.0", "end")
        response_text.insert("1.0", f"❌ Error:\n\n{error_message}")
        response_text.configure(state="disabled")


def ai_text_chat(user_message):
    """AI chatbot that can answer any text-based question"""
    conn = None
    try:
        update_status("🤖 Jarvis is thinking...")

        # Connection to AI server
        conn = http.client.HTTPSConnection("ai.recepguzel.com", timeout=60)

        # Text models to try
        models_to_try = [
            "llava:13b",  # Best quality
            "llava:7b",  # Good balance
            "llava:latest",  # Fallback
            "bakllava:latest",  # Alternative
            "llava-llama3",  # Alternative
        ]

        last_error = None

        for model_name in models_to_try:
            try:
                print(f"🔄 Trying text model: {model_name}")

                payload_data = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are Jarvis, a helpful and friendly AI assistant. You can:
- Answer questions on any topic
- Have casual conversations
- Provide explanations and help
- Be creative and engaging

Respond naturally and conversationally. Be helpful, accurate, and friendly."""
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1000,
                    }
                }

                headers = {
                    'content-type': "application/json",
                    'authorization': "Basic YWl1c2VyOkJ1QWk1UGFyYUV0bWV6IQ=="
                }

                if conn:
                    conn.close()
                conn = http.client.HTTPSConnection("ai.recepguzel.com", timeout=60)
                conn.request("POST", "/api/chat", json.dumps(payload_data), headers)

                res = conn.getresponse()

                if res.status == 200:
                    print(f"✅ Model {model_name} is responding!")

                    data = res.read()
                    result = json.loads(data.decode("utf-8"))

                    # Get response
                    full_response = result.get("message", {}).get("content", "")

                    if not full_response:
                        full_response = result.get("response", "")

                    if full_response:
                        window.after(0, lambda: update_status("✅ Response ready!"))

                        # Format response
                        formatted_response = f"""🤖 Jarvis says:

{full_response}

─────────────────────────────
⏰ {time.strftime('%H:%M:%S')}
"""
                        window.after(0, lambda r=formatted_response: update_ui_with_token(r))
                        return
                    else:
                        raise Exception(f"No response from model")
                else:
                    error_body = res.read().decode("utf-8")
                    last_error = f"Model {model_name}: Status {res.status}"
                    print(f"❌ {last_error}")
                    continue

            except Exception as e:
                last_error = f"Model {model_name}: {str(e)}"
                print(f"❌ {last_error}")
                continue

        # No models worked
        raise Exception(f"""Could not connect to AI models!

Please check:
1. Server is running
2. Models are installed (ollama pull llama3.2)
3. Network connection

Last error: {last_error}""")

    except socket.timeout:
        window.after(0, lambda: show_error("Request timeout - AI took too long to respond"))
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        window.after(0, lambda m=error_msg: show_error(f"{m}"))
    finally:
        if conn:
            conn.close()


def send_message(event=None):
    """Handle sending a message when user presses Send or Enter"""
    user_input = chatbot_input.get().strip()

    if user_input:
        # Show user message
        print(f"User: {user_input}")

        # Clear input field
        chatbot_input.delete(0, 'end')

        # Show user's message in response area
        response_text.configure(state="normal")
        response_text.delete("1.0", "end")
        response_text.insert("1.0", f"You: {user_input}\n\n{'─' * 40}\n\nJarvis is thinking...")
        response_text.configure(state="disabled")

        # Run AI in background thread to keep UI responsive
        thread = threading.Thread(target=ai_text_chat, args=(user_input,))
        thread.daemon = True
        thread.start()

    return "break"  # Prevent default Enter behavior


# ========== UI COMPONENTS ==========

theme_button = ctk.CTkButton(
    window,
    text="☀️ Light Mode",
    width=150,
    height=40,
    font=("Arial", 12),
    corner_radius=10,
    command=toggle_theme
)
theme_button.pack(pady=10)

# Header Frame
header_frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=15)
header_frame.pack(pady=20, fill="x")

# Bot Avatar
avatar_label = ctk.CTkLabel(header_frame, text="🤖", font=("Arial", 50))
avatar_label.pack(pady=(30, 10))

# Title
theme_button.pack(pady=10)

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

# Status Label (shows AI activity)
status_label = ctk.CTkLabel(
    window,
    text="",
    font=("Arial", 12),
    text_color="#4ade80"
)
status_label.pack(pady=5)

# Response Display Area (shows conversation)
response_frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=10)
response_frame.pack(pady=10, fill="both", expand=True)

response_text = ctk.CTkTextbox(
    response_frame,
    font=("Arial", 14),
    wrap="word",
    fg_color="#0a0a0a",
    corner_radius=8
)
response_text.pack(padx=10, pady=10, fill="both", expand=True)
response_text.insert("1.0",
                     "Welcome! Ask me anything...\n\nExamples:\n• How are you?\n• Tell me a joke\n• Explain quantum physics\n• What's the weather like?")
response_text.configure(state="disabled")

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
chatbot_input.bind("<Return>", send_message)  # Send on Enter key

# Send Button
send_button = ctk.CTkButton(
    input_frame,
    text="Send Message",
    width=200,
    height=50,
    font=("Arial Bold", 16),
    corner_radius=10,
    command=send_message  # Fixed: Now calls send_message function
)
send_button.pack(pady=10)

# Footer
footer_label = ctk.CTkLabel(
    window,
    text="Powered by AI Technology • Press Enter or click Send to chat",
    font=("Arial", 11),
    text_color="#5a5a5a"
)
footer_label.pack(side="bottom", pady=20)

# Start the application
window.mainloop()