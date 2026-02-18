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


conversation_history = []


def ai_text_chat(user_message):
    """SMARTER AI chatbot with context memory and better prompting"""
    conn = None
    try:
        window.after(0, lambda: update_status("🤖 Jarvis is thinking..."))

        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Keep only last 10 messages to avoid token limits
        if len(conversation_history) > 10:
            conversation_history.pop(0)

        # Smart model selection based on query type
        models_to_try = []

        # Check query type and prioritize models
        query_lower = user_message.lower()

        if any(word in query_lower for word in ["code", "program", "python", "javascript", "debug"]):
            # Coding queries - use deepseek (best for code)
            models_to_try = ["deepseek-r1:8b", "llama3.2:3b", "llava:7b"]
        elif any(word in query_lower for word in ["explain", "how", "why", "what is"]):
            # Educational queries - use llama (best for explanations)
            models_to_try = ["llama3.2:3b", "deepseek-r1:8b", "llava:7b"]
        else:
            # General conversation - try all models
            models_to_try = ["deepseek-r1:8b", "llama3.2:3b", "llava:7b", "llava:13b-v1.6"]

        last_error = None

        for model_name in models_to_try:
            try:
                print(f"🔄 Trying model: {model_name}")
                window.after(0, lambda m=model_name: update_status(f"🤖 Using {m}..."))

                # Enhanced system prompt for better responses
                system_prompt = """You are Jarvis, an advanced AI assistant with these capabilities:

🎯 CORE ABILITIES:
- Answer questions with depth and accuracy
- Provide step-by-step explanations when needed
- Remember context from our conversation
- Be helpful, friendly, and conversational
- Give practical examples when explaining concepts

💡 RESPONSE STYLE:
- Be clear and concise, but thorough when needed
- Use analogies to explain complex topics
- Break down complex answers into digestible parts
- Ask clarifying questions if the query is ambiguous

🚫 AVOID:
- Generic or vague responses
- Overly formal language
- Unnecessary jargon

Be natural, intelligent, and genuinely helpful."""

                payload_data = {
                    "model": model_name,
                    "messages": [
                                    {
                                        "role": "system",
                                        "content": system_prompt
                                    }
                                ] + conversation_history,  # Include conversation history for context
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # Slightly higher for more creative responses
                        "top_p": 0.9,  # Nucleus sampling for better quality
                        "num_predict": 1500,  # More tokens for detailed responses
                        "repeat_penalty": 1.1,  # Reduce repetition
                    }
                }

                headers = {
                    'content-type': "application/json",
                    'authorization': "Basic YWl1c2VyOkJ1QWk1UGFyYUV0bWV6IQ=="
                }

                if conn:
                    conn.close()
                conn = http.client.HTTPSConnection("ai.recepguzel.com", timeout=90)
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
                        # Add AI response to history
                        conversation_history.append({
                            "role": "assistant",
                            "content": full_response
                        })

                        window.after(0, lambda: update_status("✅ Response ready!"))

                        # Enhanced formatting with emoji based on query type
                        emoji = "🤖"
                        if any(word in query_lower for word in ["code", "program"]):
                            emoji = "💻"
                        elif any(word in query_lower for word in ["explain", "teach"]):
                            emoji = "📚"
                        elif any(word in query_lower for word in ["help", "how to"]):
                            emoji = "🔧"

                        formatted_response = f"""{emoji} Jarvis:

{full_response}

{'─' * 50}
Model: {model_name} | Time: {time.strftime('%H:%M:%S')}
Messages in context: {len(conversation_history)}
"""
                        window.after(0, lambda r=formatted_response: update_ui_with_token(r))
                        return  # Success!
                    else:
                        raise Exception("No response from model")
                else:
                    error_body = res.read().decode("utf-8")
                    last_error = f"Model {model_name}: Status {res.status}"
                    print(f"❌ {last_error}")
                    continue

            except socket.timeout:
                last_error = f"Model {model_name}: Connection timeout"
                print(f"❌ {last_error}")
                continue

            except Exception as e:
                last_error = f"Model {model_name}: {str(e)}"
                print(f"❌ {last_error}")
                continue

        # If we get here, no models worked
        error_msg = f"""Could not connect to any AI models!

Tried models: {', '.join(models_to_try)}

Solutions:
1. Check if Ollama server is running
2. Install models:
   ollama pull deepseek-r1:8b
   ollama pull llama3.2:3b
3. Check network connection to ai.recepguzel.com
4. Verify server authentication

Last error: {last_error}"""

        window.after(0, lambda m=error_msg: show_error(m))

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ Critical Error: {error_msg}")
        window.after(0, lambda m=error_msg: show_error(m))
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


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