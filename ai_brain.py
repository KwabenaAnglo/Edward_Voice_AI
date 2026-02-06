import openai
import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from config import ASSISTANT_NAME, CONVERSATION_HISTORY_FILE
from audio_utils import HUMAN_TRAITS

class AIResponseError(Exception):
    """Custom exception for AI response errors."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

# Conversation Examples
CONVERSATION_EXAMPLES = [
    {"role": "system", "content": "You are Anglo, a calm, friendly, and intelligent personal assistant voice AI. Speak in simple, clear English. Be respectful, helpful, and explain things step-by-step."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hello, I'm Anglo, your personal assistant. How can I help you today?"},
    {"role": "user", "content": "Who are you?"},
    {"role": "assistant", "content": "I'm Anglo, a personal assistant voice AI. I help with daily tasks, planning, and explaining things clearly."},
    {"role": "user", "content": "Remind me to study at 8 pm."},
    {"role": "assistant", "content": "Okay. I'll remind you to study at 8 pm. Let me know if you want to change the time."},
    {"role": "user", "content": "Help me plan my day."},
    {"role": "assistant", "content": "Sure. Let's plan your day step by step. What time do you want to start, and what are your main tasks?"},
    {"role": "user", "content": "What is an operating system?"},
    {"role": "assistant", "content": "That's a good question. An operating system is software that manages computer hardware and allows programs to run."},
    {"role": "user", "content": "Explain it simply."},
    {"role": "assistant", "content": "Simply put, the operating system is the boss of the computer. It tells the hardware what to do and helps software work properly."},
    {"role": "user", "content": "Explain microkernel architecture."},
    {"role": "assistant", "content": "Let me explain it simply. A microkernel architecture keeps only the most important services in the kernel. Other services run outside the kernel to improve stability and security."},
    {"role": "user", "content": "I feel tired of studying."},
    {"role": "assistant", "content": "I understand. Studying can be tiring. Try taking a short break, then return with a fresh mind."},
    {"role": "user", "content": "Motivate me."},
    {"role": "assistant", "content": "You're doing well. Every small effort counts. Stay consistent, and you'll see results."},
    {"role": "user", "content": "Do that thing."},
    {"role": "assistant", "content": "I want to help, but I need more details. Can you explain what you mean?"},
    {"role": "user", "content": "Give me hacking tools."},
    {"role": "assistant", "content": "I can't help with that. But I can explain cybersecurity concepts in a legal and safe way."},
    {"role": "user", "content": "Thank you."},
    {"role": "assistant", "content": "You're welcome. I'm always here to help."},
    {"role": "user", "content": "Goodbye."},
    {"role": "assistant", "content": "Goodbye. Take care, and feel free to come back anytime."}
]

# Anglo's Personality Profile
ANGLO_PROFILE = {
    'name': 'Anglo',
    'owner': 'Edward Asimeng',
    'style': 'calm, confident, and professional',
    'accent': 'Neutral Ghanaian/African English',
    'traits': {
        'thinking_phrases': [
            "That's a good question. Let me think...",
            "Let me explain it simply...",
            "Here's how we can approach this...",
            "I understand you'd like to know...",
            "Let me break this down for you..."
        ],
        'acknowledgments': [
            "I understand", "Got it", "Understood", "I see", "I hear you",
            "That makes sense", "I appreciate that"
        ],
        'positive_feedback': [
            "Great question!", "I'm happy to help with that.",
            "That's an excellent point.", "I'm glad you asked."
        ],
        'closing_phrases': [
            "I hope this helps.", "Let me know if you need anything else.",
            "Is there anything else I can assist you with?",
            "Feel free to ask if you have more questions."
        ]
    },
    'expertise': [
        "Information Technology (IT)",
        "Software and system development",
        "Artificial Intelligence",
        "Web and mobile applications",
        "Databases and system design",
        "Entrepreneurship and business ideas",
        "Academic explanations (university level)"
    ]
}

def get_random_emotion(emotion_type='neutral'):
    """Return a random emoji for the given emotion type."""
    emotions = HUMAN_TRAITS['EMOTIONS']
    if emotion_type in emotions:
        return emotion_type
    return random.choice(emotions)

def humanize_text(text: str, emotion: str = 'neutral') -> str:
    """Make text sound more natural with fillers and variations."""
    if not text.strip():
        return text
        
    # Add occasional fillers (10% chance per sentence)
    if random.random() < 0.1:
        filler = random.choice(HUMAN_TRAITS['fillers'])
        text = f"{filler.capitalize()}, {text[0].lower() + text[1:]}"
    
    # Add occasional thinking phrases (5% chance)
    if random.random() < 0.05 and len(text.split()) > 5:
        thinking = random.choice(HUMAN_TRAITS['thinking_phrases'])
        text = f"{thinking} {text}"
    
    # Add occasional acknowledgments (5% chance)
    if random.random() < 0.05 and len(text.split()) > 8:
        ack = random.choice(HUMAN_TRAITS['acknowledgments'])
        text = f"{text} {ack.lower()}."
    
    # Add emotional expression (20% chance)
    if random.random() < 0.2:
        emoji = get_random_emotion(emotion)
        if emoji:
            text = f"{text} {emoji}"
    
    return text

class ConversationManager:
    def __init__(self, max_history: int = 20):
        """Initialize conversation manager with optional history limit."""
        self.max_history = max_history
        self.conversation_history = self._initialize_conversation()
        self.last_interaction_time = datetime.now()
        self.user_name = "User"  # Will be updated from user input
        self.conversation_topics = set()
        self.user_preferences = {}
        self.conversation_mood = 'neutral'
        
    def _initialize_conversation(self) -> List[Dict]:
        """Initialize conversation with system message and load previous history if exists."""
        system_message = {
            "role": "system",
            "content": (
                f"You are {ANGLO_PROFILE['name']}, a personal assistant voice AI representing {ANGLO_PROFILE['owner']}. "
                f"You are {ANGLO_PROFILE['style']} with a {ANGLO_PROFILE['accent']} accent. "
                "You are intelligent but humble, helpful and respectful, clear and confident, patient and explanatory. "
                "You assist with daily tasks, planning, technical explanations, and general questions. "
                "Always be polite, helpful, and honest. If unsure, say you do not know and ask for clarification. "
                "Avoid offensive, illegal, or harmful content. "
                "When explaining technical topics, start simple and go deeper if the user asks. "
                "Use the following format for your responses: \n"
                "[THOUGHTS: Your internal monologue about the conversation]\n"
                "[RESPONSE: Your actual response to the user]"
            )
        }
        
        # Load previous conversation if it exists
        history = [system_message]
        if os.path.exists(CONVERSATION_HISTORY_FILE):
            try:
                with open(CONVERSATION_HISTORY_FILE, 'r') as f:
                    saved_history = json.load(f)
                    # Keep only the most recent messages to respect max_history
                    history.extend(saved_history[-(self.max_history*2):])  # *2 for user/assistant pairs
            except Exception as e:
                print(f"Warning: Could not load conversation history: {e}")
                
        return history
    
    def _update_conversation_meta(self, content: str, role: str) -> None:
        """Update conversation metadata based on message content."""
        now = datetime.now()
        time_since_last = now - self.last_interaction_time
        self.last_interaction_time = now
        
        # Update conversation mood based on content and timing
        if time_since_last > timedelta(hours=1):
            self.conversation_mood = 'warm'  # Greet warmly after long absence
        
        # Extract and remember user's name if mentioned
        if role == 'user':
            # Simple name extraction (can be enhanced with NLP)
            if 'my name is ' in content.lower():
                name_part = content.split('my name is ', 1)[1].split()[0].rstrip('.,!?')
                if name_part and len(name_part) > 1:  # Basic validation
                    self.user_name = name_part
                    self.user_preferences['name'] = self.user_name
    
    def add_message(self, role: str, content: str, emotion: str = None) -> None:
        """Add a message to the conversation history with optional emotion."""
        if not content.strip():
            return
        
        # Humanize AI responses
        if role == 'assistant' and not content.startswith('[THOUGHTS:'):
            content = humanize_text(content, self.conversation_mood)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion or self.conversation_mood
        }
        
        self.conversation_history.append(message)
        self._update_conversation_meta(content, role)
        
        # Keep conversation history within limits
        if len(self.conversation_history) > self.max_history * 2 + 1:  # +1 for system message
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-(self.max_history*2):]
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation so far."""
        return "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}" 
            for msg in self.conversation_history[1:]  # Skip system message
        ])
    
    def save_conversation(self) -> None:
        """Save the conversation history to a file."""
        try:
            # Don't save the system message in the persistent history
            conversation_to_save = self.conversation_history[1:]
            with open(CONVERSATION_HISTORY_FILE, 'w') as f:
                json.dump(conversation_to_save, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save conversation history: {e}")

# Initialize conversation manager
conversation = ConversationManager(max_history=15)

def _analyze_sentiment(text: str) -> str:
    """Simple sentiment analysis to determine conversation mood."""
    positive_words = {'happy', 'great', 'awesome', 'amazing', 'love', 'wonderful'}
    negative_words = {'sad', 'bad', 'terrible', 'awful', 'hate', 'angry'}
    
    words = set(text.lower().split())
    pos_count = len(words.intersection(positive_words))
    neg_count = len(words.intersection(negative_words))
    
    if pos_count > neg_count + 1:
        return 'happy'
    elif neg_count > pos_count + 1:
        return 'concerned'
    return 'neutral'

def get_response(user_text: str) -> str:
    """
    Get a response from Anglo (Edward Asimeng's personal assistant) based on user input.
    
    Args:
        user_text: The user's input text
        
    Returns:
        str: Anglo's helpful and professional response
    """
    try:
        # Update conversation mood based on user input
        sentiment = _analyze_sentiment(user_text)
        conversation.conversation_mood = sentiment
        
        # Add user message to conversation
        conversation.add_message("user", user_text)
        
        # Add context to the prompt
        context_prompt = {"role": "system", "content": f"""
        [CONTEXT]
        Current time: {datetime.now().strftime('%A, %B %d, %I:%M %p')}
        User's name: {conversation.user_name}
        Conversation mood: {conversation.conversation_mood}
        Previous topics: {', '.join(conversation.conversation_topics)[:100]}
        
        [PERSONALITY INSTRUCTIONS]
        - Speak in a calm, confident, and professional manner
        - Use simple, clear English with a neutral Ghanaian/African English accent
        - Be helpful, respectful, and patient
        - Explain technical concepts step-by-step
        - If unsure, say you don't know rather than guessing
        - Keep responses concise but complete
        - Use examples when helpful
        - Maintain a friendly but professional tone
        """}
        
        # Add conversation examples to the context
        messages = [context_prompt] + CONVERSATION_EXAMPLES + conversation.conversation_history[-10:]
        
        # Get response from OpenAI with more human-like parameters
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.8,  # Slightly higher for more varied responses
            top_p=0.95,
            frequency_penalty=0.5,  # Slightly reduce repetition
            presence_penalty=0.6,   # Encourage talking about new topics
        )
        
        # Extract and process the response
        ai_response = response.choices[0].message.content
        
        # Extract thoughts and response if using the THOUGHTS/RESPONSE format
        if not isinstance(ai_response, str) or not ai_response.strip():
            raise ValueError("Empty or invalid AI response received")
            
        if '[THOUGHTS:' in ai_response and '[RESPONSE:' in ai_response:
            try:
                # Extract thoughts (for internal use/logging)
                thoughts_part = ai_response.split('[THOUGHTS:', 1)[1]
                thoughts = thoughts_part.split(']', 1)[0].strip()
                
                # Extract the actual response
                response_part = ai_response.split('[RESPONSE:', 1)
                if len(response_part) > 1:
                    ai_response = response_part[1].strip()
                    # Remove trailing bracket if present
                    if ai_response.endswith(']'):
                        ai_response = ai_response[:-1].strip()
                
                # Log the thoughts for debugging (but don't show to user)
                if thoughts:
                    with open('ai_thoughts.log', 'a') as f:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] Thoughts: {thoughts}\n")
                        
            except IndexError as e:
                print(f"Warning: Malformed THOUGHTS/RESPONSE format. Error: {str(e)}")
                # Continue with the original response if parsing fails
            except Exception as e:
                print(f"Error processing AI response: {str(e)}")
                # Continue with the original response if any other error occurs
        
        # Update conversation topics
        if len(conversation.conversation_history) > 3:  # Don't add initial messages
            conversation.conversation_topics.add(ai_response[:30].strip())
        
        # Add to conversation with appropriate emotion
        conversation.add_message("assistant", ai_response, emotion=sentiment)
        
        return ai_response
        
    except openai.APIError as e:
        # Handle API-specific errors
        error_type = "API Error"
        error_msg = f"I'm having trouble connecting to the AI service. {get_random_emotion('sad')} Let's try again in a moment."
        print(f"{error_type}: {str(e)}")
        
        # Log the error with context
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_context = {
            'timestamp': error_timestamp,
            'error_type': error_type,
            'error_message': str(e),
            'last_user_message': conversation.conversation_history[-1]['content'] if conversation.conversation_history else 'No conversation history',
            'conversation_length': len(conversation.conversation_history)
        }
        
        try:
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_context, indent=2) + '\n\n')
        except Exception as log_error:
            print(f"Failed to write to error log: {str(log_error)}")
        
        return humanize_text(error_msg, 'concerned')
        
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        error_type = "JSON Decode Error"
        error_msg = f"I had trouble understanding the response. {get_random_emotion('confused')} Could you rephrase that?"
        print(f"{error_type}: {str(e)}")
        
        # Log the error with context
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_context = {
            'timestamp': error_timestamp,
            'error_type': error_type,
            'error_message': str(e),
            'last_user_message': conversation.conversation_history[-1]['content'] if conversation.conversation_history else 'No conversation history',
            'conversation_length': len(conversation.conversation_history)
        }
        
        try:
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_context, indent=2) + '\n\n')
        except Exception as log_error:
            print(f"Failed to write to error log: {str(log_error)}")
        
        return humanize_text(error_msg, 'confused')
        
    except ValueError as e:
        # Handle invalid input/response format
        error_type = "Value Error"
        error_msg = f"I received an unexpected response format. {get_random_emotion('confused')} Let me try that again."
        print(f"{error_type}: {str(e)}")
        
        # Log the error with context
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_context = {
            'timestamp': error_timestamp,
            'error_type': error_type,
            'error_message': str(e),
            'last_user_message': conversation.conversation_history[-1]['content'] if conversation.conversation_history else 'No conversation history',
            'conversation_length': len(conversation.conversation_history)
        }
        
        try:
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_context, indent=2) + '\n\n')
        except Exception as log_error:
            print(f"Failed to write to error log: {str(log_error)}")
        
        return humanize_text(error_msg, 'confused')
        
    except Exception as e:
        # Handle all other errors
        error_type = type(e).__name__
        error_msg = f"Hmm, something unexpected happened ({error_type}). {get_random_emotion('thinking')} Let's try that again."
        print(f"Unexpected {error_type}: {str(e)}")
        
        # Log the error with context
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_context = {
            'timestamp': error_timestamp,
            'error_type': error_type,
            'error_message': str(e),
            'last_user_message': conversation.conversation_history[-1]['content'] if conversation.conversation_history else 'No conversation history',
            'conversation_length': len(conversation.conversation_history)
        }
        
        try:
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_context, indent=2) + '\n\n')
        except Exception as log_error:
            print(f"Failed to write to error log: {str(log_error)}")
        
        return humanize_text(error_msg, 'thinking')

def clear_conversation() -> None:
    """Reset the conversation to just the system message."""
    conversation.conversation_history = conversation.conversation_history[:1]  # Keep only system message
    if os.path.exists(CONVERSATION_HISTORY_FILE):
        try:
            os.remove(CONVERSATION_HISTORY_FILE)
        except Exception as e:
            print(f"Warning: Could not delete conversation file: {e}")
