"""
GUI Module for Edward Voice AI

This module provides the graphical user interface for the Edward Voice AI application.
It handles user interactions and displays the conversation history.
"""
import logging
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import Optional, Callable, Any

# Import local modules
from config import ConfigError
from voice_input import record_voice
from speech_to_text import speech_to_text, SpeechRecognitionError
from ai_brain import get_response, clear_conversation, AIResponseError
from text_to_speech import speak, TTSConversionError
from utils.error_handler import (
    handle_error,
    handle_gui_error,
    VoiceAIError,
    AudioError,
    APIConnectionError
)

# Set up logging
logger = logging.getLogger(__name__)

class EdwardGUI:
    """Main GUI class for Edward Voice AI."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.setup_ui()
        self.is_recording = False
        self.recording_thread = None
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("GUI initialized")

    @handle_error((tk.TclError, AttributeError), "Failed to update status")
    def update_status(self, message: str, color: str = 'black') -> None:
        """Update the status bar with a message.
        
        Args:
            message: The message to display
            color: Text color for the status message
        """
        if not hasattr(self, 'status_var'):
            logger.warning("Status var not initialized")
            return
            
        try:
            self.status_var.set(message)
            self.status_label.config(fg=color)
            self.root.update_idletasks()
            logger.debug("Status updated: %s", message)
        except tk.TclError as e:
            logger.error("Failed to update status: %s", str(e))
            raise

    @handle_gui_error()
    def clear_chat(self) -> None:
        """Clear the conversation history."""
        if messagebox.askyesno("Clear Conversation", "Are you sure you want to clear the conversation?"):
            try:
                self.chat.config(state=tk.NORMAL)
                self.chat.delete(1.0, tk.END)
                clear_conversation()
                self.update_status("Conversation cleared", 'green')
                logger.info("Conversation cleared by user")
            except Exception as e:
                logger.error("Failed to clear conversation: %s", str(e))
                raise VoiceAIError("Failed to clear conversation") from e

    @handle_gui_error()
    def process_voice(self) -> None:
        """Handle the voice recording and processing."""
        if not self.is_recording:
            self.is_recording = True
            self.record_button.config(text="Stop Recording", fg='red')
            self.update_status("Listening... (speak now)", 'blue')
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(
                target=self._process_voice_thread,
                daemon=True
            )
            self.recording_thread.start()
        else:
            self.is_recording = False
            self.update_status("Stopping recording...", 'orange')
    
    def _process_voice_thread(self) -> None:
        """Background thread for processing voice input."""
        try:
            # Record audio
            audio_file = record_voice(stop_event=lambda: not self.is_recording)
            
            if not audio_file:
                self.update_status("No audio recorded", 'orange')
                return
                
            self.update_status("Processing your request...", 'blue')
            
            # Convert speech to text
            try:
                text = speech_to_text(audio_file)
                if not text:
                    self.update_status("Could not transcribe audio", 'orange')
                    return
                    
                self._update_chat(f"You: {text}\n")
                
                # Get AI response
                response = get_response(text)
                if response:
                    self._update_chat(f"{self.assistant_name.get()}: {response}")
                    speak(response)
                
                self.update_status("Ready", 'green')
                
            except SpeechRecognitionError as e:
                self.update_status(f"Speech recognition error: {str(e)}", 'red')
                logger.error("Speech recognition failed: %s", str(e))
                
            except AIResponseError as e:
                self.update_status(f"AI service error: {str(e)}", 'red')
                logger.error("AI response generation failed: %s", str(e))
                
            except TTSConversionError as e:
                self.update_status(f"Speech synthesis error: {str(e)}", 'red')
                logger.error("Text-to-speech conversion failed: %s", str(e))
                
        except AudioError as e:
            self.update_status(f"Audio error: {str(e)}", 'red')
            logger.error("Audio processing error: %s", str(e))
            
        except APIConnectionError as e:
            self.update_status("Connection error. Please check your internet connection.", 'red')
            logger.error("API connection error: %s", str(e))
            
        except Exception as e:
            self.update_status("An unexpected error occurred", 'red')
            logger.error("Unexpected error in voice processing: %s", str(e), exc_info=True)
            
        finally:
            self.is_recording = False
            self.root.after(0, self._reset_record_button)
    
    def _update_chat(self, message: str) -> None:
        """Update the chat display with a new message."""
        try:
            self.chat.config(state=tk.NORMAL)
            self.chat.insert(tk.END, message + "\n")
            self.chat.see(tk.END)
            self.chat.config(state=tk.DISABLED)
        except tk.TclError as e:
            logger.error("Failed to update chat: %s", str(e))
            raise VoiceAIError("Failed to update chat display") from e
    
    def _reset_record_button(self) -> None:
        """Reset the record button to its default state."""
        try:
            self.record_button.config(text="Record Voice", fg='black')
        except tk.TclError as e:
            logger.warning("Failed to reset record button: %s", str(e))
    
    def setup_ui(self) -> None:
        """Set up the user interface components."""
        try:
            # Configure window
            self.root.geometry("800x600")
            self.root.minsize(600, 400)
            
            # Create main frame
            main_frame = tk.Frame(self.root, padx=10, pady=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Chat display
            self.chat = scrolledtext.ScrolledText(
                main_frame,
                wrap=tk.WORD,
                width=80,
                height=25,
                state=tk.DISABLED,
                font=('Segoe UI', 10)
            )
            self.chat.pack(pady=(0, 10), fill=tk.BOTH, expand=True)
            
            # Input frame
            input_frame = tk.Frame(main_frame)
            input_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Text input
            self.input_box = tk.Entry(input_frame, font=('Segoe UI', 10))
            self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            self.input_box.bind('<Return>', self.on_key_press)
            
            # Send button
            self.send_button = tk.Button(
                input_frame,
                text="Send",
                command=self.interact,
                width=10
            )
            self.send_button.pack(side=tk.RIGHT)
            
            # Button frame
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Assistant name
            tk.Label(button_frame, text="Assistant Name:").pack(side=tk.LEFT, padx=(0, 5))
            self.assistant_name = tk.StringVar(value="Edward")
            name_entry = tk.Entry(
                button_frame,
                textvariable=self.assistant_name,
                width=15
            )
            name_entry.pack(side=tk.LEFT, padx=(0, 10))
            
            # Record button
            self.record_button = tk.Button(
                button_frame,
                text="Record Voice",
                command=self.process_voice,
                width=15
            )
            self.record_button.pack(side=tk.LEFT, padx=5)
            
            # Clear button
            clear_button = tk.Button(
                button_frame,
                text="Clear Chat",
                command=self.clear_chat,
                width=15
            )
            clear_button.pack(side=tk.LEFT, padx=5)
            
            # Status bar
            self.status_var = tk.StringVar()
            self.status_var.set("Ready")
            self.status_label = tk.Label(
                self.root,
                textvariable=self.status_var,
                bd=1,
                relief=tk.SUNKEN,
                anchor=tk.W,
                font=('Segoe UI', 9)
            )
            self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Configure grid weights
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)
            
            logger.debug("UI setup completed")
            
        except tk.TclError as e:
            logger.critical("Failed to set up UI: %s", str(e))
            raise VoiceAIError("Failed to initialize user interface") from e
    
    def on_key_press(self, event) -> None:
        """Handle keyboard events."""
        try:
            if event.keysym == 'Return':
                # Handle Enter key press in the input box
                if event.widget == self.input_box:
                    self.interact()
            elif event.keysym == 'Escape':
                self.on_closing()
            elif event.keysym == 'space':
                # Handle space key for voice recording
                if hasattr(self, 'record_button') and self.record_button['state'] == 'normal':
                    self.process_voice()
        except Exception as e:
            logger.error("Error handling key press: %s", str(e))
    
    def interact(self, event=None) -> None:
        """Handle user interaction with the chat interface."""
        try:
            # Get user input
            user_input = self.input_box.get().strip()
            if not user_input:
                return
                
            # Clear input box
            self.input_box.delete(0, tk.END)
            
            # Update chat with user message
            self._update_chat(f"You: {user_input}")
            
            # Get AI response
            try:
                from ai_brain import get_response
                response = get_response(user_input)
                self._update_chat(f"{self.assistant_name.get()}: {response}")
                
                # Speak the response
                from text_to_speech import speak
                speak(response)
                
            except ImportError as e:
                self.update_status(f"Error: {str(e)}", 'red')
                logger.error("Failed to import required modules: %s", str(e))
                
        except Exception as e:
            logger.error("Error in interact method: %s", str(e), exc_info=True)
            self.update_status(f"Error: {str(e)}", 'red')
    
    def on_closing(self) -> None:
        """Handle window close event."""
        try:
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                logger.info("Application closing...")
                self.root.quit()
        except Exception as e:
            logger.error("Error during application shutdown: %s", str(e))
            self.root.quit()

def on_key_press(event):
    """Handle keyboard shortcuts."""
    if event.keysym == 'Escape':
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            event.widget.quit()
    elif event.keysym == 'space' and hasattr(event.widget, 'record_button') and event.widget.record_button['state'] == 'normal':
        event.widget.process_voice()

def main():
    """Main entry point for the GUI application."""
    try:
        # Create main window
        window = tk.Tk()
        window.title("Edward – Personal Voice AI")
        
        # Bind keyboard shortcuts
        window.bind('<Key>', on_key_press)
        
        # Create the main application
        app = EdwardGUI(window)
        
        # Set up window close handler
        window.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start the main event loop
        window.mainloop()
        
    except Exception as e:
        logger.critical("Fatal error in main application: %s", str(e), exc_info=True)
        messagebox.showerror("Error", f"A fatal error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
