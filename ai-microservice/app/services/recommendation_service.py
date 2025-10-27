"""
Music Recommendation Service using GPT-4
"""
import openai
from ..config import settings

class RecommendationService:
    """Service for generating music recommendations based on chat history"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def get_recommendation(self, chat_history: list) -> dict:
        """
        Generate music recommendation based on chat history
        
        Args:
            chat_history: List of previous chat messages
            
        Returns:
            Dict with recommendation details
        """
        try:
            # Extract songs mentioned in chat history
            songs_mentioned = self._extract_songs(chat_history)
            
            prompt = f"""
            Based on this chat history, recommend a similar song:
            
            Chat History: {chat_history}
            Songs Mentioned: {songs_mentioned}
            
            Requirements:
            1. Recommend ONE song that would be appropriate for music teachers
            2. Consider the difficulty level and style of mentioned songs
            3. Choose songs suitable for students
            4. Provide reasoning for your recommendation
            5. Return in this JSON format:
            {{
                "recommendation": "Song Name",
                "artist": "Artist Name",
                "reasoning": "Brief explanation of why this song fits"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a music teacher's assistant. Recommend appropriate songs for students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                # Clean up the response
                if result_text.startswith('```'):
                    result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                
                recommendation = json.loads(result_text)
                return recommendation
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'recommendation': 'Twinkle Twinkle Little Star',
                    'artist': 'Traditional',
                    'reasoning': 'A classic beginner song suitable for all students'
                }
            
        except Exception as e:
            raise Exception(f"Recommendation failed: {str(e)}")
    
    def _extract_songs(self, chat_history: list) -> list:
        """Extract song names from chat history"""
        songs = []
        for message in chat_history:
            if isinstance(message, dict) and 'song' in message:
                songs.append(message['song'])
            elif isinstance(message, dict) and 'text' in message:
                # Try to extract song names from text
                text = message['text'].lower()
                if any(keyword in text for keyword in ['song', 'music', 'melody']):
                    songs.append(message['text'])
        return songs
