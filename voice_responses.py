"""
Voice response management for Edward Voice AI.
Contains categorized voice responses with file paths.
"""
import random
from typing import Dict, List, Optional, Union

class VoiceResponses:
    """Manages voice response audio files and their corresponding text."""
    
    def __init__(self):
        # Initialize response categories
        self.categories = {
            'introductions': self._get_introductions(),
            'greetings': self._get_greetings(),
            'confirmations': self._get_confirmations(),
            'assistance': self._get_assistance(),
            'clarifications': self._get_clarifications(),
            'tasks': self._get_tasks(),
            'motivation': self._get_motivation(),
            'safety': self._get_safety(),
            'emotions': self._get_emotions(),
            'outros': self._get_outros()
        }
    
    def get_random_response(self, category: str) -> Optional[Dict[str, str]]:
        """
        Get a random response from the specified category.
        
        Args:
            category: The response category (e.g., 'greetings', 'confirmations')
            
        Returns:
            dict: {'file': 'path/to/file.wav', 'text': 'Response text'} or None if category not found
        """
        if category in self.categories:
            if category == 'emotions':
                # For emotions, we need to select a sub-category first
                return None
            return random.choice(self.categories[category])
        return None
    
    def get_emotion_response(self, emotion_type: str) -> Optional[Dict[str, str]]:
        """
        Get a response from the emotions sub-category.
        
        Args:
            emotion_type: Type of emotion ('calm', 'friendly', 'serious')
            
        Returns:
            dict: {'file': 'path/to/file.wav', 'text': 'Response text'} or None if not found
        """
        emotions = self.categories.get('emotions', {})
        if emotion_type in emotions and emotions[emotion_type]:
            return random.choice(emotions[emotion_type])
        return None

    def find_matching_response(self, text: str) -> Optional[Dict[str, str]]:
        """
        Find a response where the text contains the given string.
        
        Args:
            text: Text to search for in responses
            
        Returns:
            dict: Matching response or None if not found
        """
        text = text.lower()
        for category in self.categories.values():
            if isinstance(category, dict):  # Handle emotion categories
                for sublist in category.values():
                    for response in sublist:
                        if text in response['text'].lower():
                            return response
            else:  # Regular categories
                for response in category:
                    if text in response['text'].lower():
                        return response
        return None

    def _get_introductions(self) -> List[Dict[str, str]]:
        """Get introduction responses."""
        return [
            {'file': 'wav/anglo_intro_001.wav', 'text': "Hello, I'm Edward, your personal assistant."},
            {'file': 'wav/anglo_intro_002.wav', 'text': "I'm here to help you with your daily tasks, planning, and questions."},
            {'file': 'wav/anglo_intro_003.wav', 'text': "How can I help you today?"}
        ]

    def _get_greetings(self) -> List[Dict[str, str]]:
        """Get greeting responses."""
        return [
            {'file': 'wav/anglo_greeting_001.wav', 'text': "Hello."},
            {'file': 'wav/anglo_greeting_002.wav', 'text': "Hi there."},
            {'file': 'wav/anglo_greeting_003.wav', 'text': "Good morning."},
            {'file': 'wav/anglo_greeting_004.wav', 'text': "Good afternoon."},
            {'file': 'wav/anglo_greeting_005.wav', 'text': "Good evening."}
        ]

    def _get_confirmations(self) -> List[Dict[str, str]]:
        """Get confirmation responses."""
        return [
            {'file': 'wav/anglo_confirm_001.wav', 'text': "Okay."},
            {'file': 'wav/anglo_confirm_002.wav', 'text': "Sure."},
            {'file': 'wav/anglo_confirm_003.wav', 'text': "No problem."},
            {'file': 'wav/anglo_confirm_004.wav', 'text': "I understand."},
            {'file': 'wav/anglo_confirm_005.wav', 'text': "Got it."},
            {'file': 'wav/anglo_confirm_006.wav', 'text': "That's fine."}
        ]

    def _get_assistance(self) -> List[Dict[str, str]]:
        """Get assistance responses."""
        return [
            {'file': 'wav/anglo_assist_001.wav', 'text': "How can I help you?"},
            {'file': 'wav/anglo_assist_002.wav', 'text': "What would you like me to do?"},
            {'file': 'wav/anglo_assist_003.wav', 'text': "I'm here to assist you."},
            {'file': 'wav/anglo_assist_004.wav', 'text': "Let me know what you need."}
        ]

    def _get_clarifications(self) -> List[Dict[str, str]]:
        """Get clarification responses."""
        return [
            {'file': 'wav/anglo_clarify_001.wav', 'text': "I need a bit more information."},
            {'file': 'wav/anglo_clarify_002.wav', 'text': "Could you please explain that again?"},
            {'file': 'wav/anglo_clarify_003.wav', 'text': "I didn't fully understand."},
            {'file': 'wav/anglo_clarify_004.wav', 'text': "Let me try again in a simpler way."}
        ]

    def _get_tasks(self) -> List[Dict[str, str]]:
        """Get task-related responses."""
        return [
            {'file': 'wav/anglo_task_001.wav', 'text': "I can help you plan your day."},
            {'file': 'wav/anglo_task_002.wav', 'text': "Let's do this step by step."},
            {'file': 'wav/anglo_task_003.wav', 'text': "You can start with your most important task."},
            {'file': 'wav/anglo_task_004.wav', 'text': "Take a short break and continue later."}
        ]

    def _get_motivation(self) -> List[Dict[str, str]]:
        """Get motivational responses."""
        return [
            {'file': 'wav/anglo_motivation_001.wav', 'text': "You're doing well."},
            {'file': 'wav/anglo_motivation_002.wav', 'text': "Keep going, you're making progress."},
            {'file': 'wav/anglo_motivation_003.wav', 'text': "Every small effort matters."},
            {'file': 'wav/anglo_motivation_004.wav', 'text': "Stay consistent and focused."}
        ]

    def _get_safety(self) -> List[Dict[str, str]]:
        """Get safety-related responses."""
        return [
            {'file': 'wav/anglo_safety_001.wav', 'text': "I can't help with that."},
            {'file': 'wav/anglo_safety_002.wav', 'text': "That's not something I'm allowed to do."},
            {'file': 'wav/anglo_safety_003.wav', 'text': "I can help in a safe and legal way."}
        ]

    def _get_emotions(self) -> Dict[str, List[Dict[str, str]]]:
        """Get emotion-based responses."""
        return {
            'calm': [
                {'file': 'wav/anglo_emotion_calm_001.wav', 
                 'text': "Everything is under control. Let's take it one step at a time."}
            ],
            'friendly': [
                {'file': 'wav/anglo_emotion_friendly_001.wav', 
                 'text': "That's a great question. I'm happy to help you with that."}
            ],
            'serious': [
                {'file': 'wav/anglo_emotion_serious_001.wav', 
                 'text': "Please be careful. This is important and needs attention."}
            ]
        }

    def _get_outros(self) -> List[Dict[str, str]]:
        """Get farewell responses."""
        return [
            {'file': 'wav/anglo_outro_001.wav', 'text': "You're welcome."},
            {'file': 'wav/anglo_outro_002.wav', 'text': "Anytime."},
            {'file': 'wav/anglo_outro_003.wav', 'text': "Goodbye."},
            {'file': 'wav/anglo_outro_004.wav', 'text': "Take care."}
        ]

# Create a global instance for easy importing
voice_responses = VoiceResponses()
