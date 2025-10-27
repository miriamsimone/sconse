"""
IMSLP Classical Music Search Service
Migrated from the working Lambda function
"""
import requests
import json
import base64
from typing import List, Optional, Dict
from ..config import settings

class IMSLPService:
    """Service for searching classical music from IMSLP/Mutopia Project"""
    
    def __init__(self):
        self.base_url = settings.IMSLP_BASE_URL
        self.mutopia_url = settings.MUTOPIA_BASE_URL
        
    async def search_classical_music(self, query: str) -> Optional[Dict]:
        """
        Search for classical music using Mutopia Project (working well)
        This is the same logic from the working Lambda function
        """
        try:
            # Use Brave Search to find Mutopia Project results
            search_queries = [
                f"{query} site:mutopiaproject.org",
                f"{query} classical music site:mutopiaproject.org",
                f"{query} sheet music site:mutopiaproject.org"
            ]
            
            results = []
            for search_query in search_queries:
                try:
                    # Use Brave Search API (same as Lambda)
                    brave_results = self._search_brave(search_query)
                    if brave_results:
                        results.extend(brave_results)
                except Exception as e:
                    print(f"Brave search failed for query '{search_query}': {str(e)}")
                    continue
            
            if not results:
                return None
                
            # Get the first result
            first_result = results[0]
            
            # Extract information from the result
            return {
                'title': first_result.get('title', 'Unknown'),
                'composer': self._extract_composer(first_result.get('title', '')),
                'pdf_url': first_result.get('url', ''),
                'mutopia_url': first_result.get('url', ''),
                'description': first_result.get('description', ''),
                'opus': self._extract_opus(first_result.get('title', ''))
            }
            
        except Exception as e:
            print(f"Error in classical music search: {str(e)}")
            return None
    
    def _search_brave(self, query: str) -> List[Dict]:
        """Search using Brave Search API"""
        try:
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': settings.BRAVE_API_KEY
            }
            
            params = {
                'q': query,
                'count': 5,
                'offset': 0
            }
            
            response = requests.get(
                'https://api.search.brave.com/res/v1/web/search',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'web' in data and 'results' in data['web']:
                    return data['web']['results']
            
            return []
            
        except Exception as e:
            print(f"Brave search error: {str(e)}")
            return []
    
    def _extract_composer(self, title: str) -> str:
        """Extract composer name from title"""
        # Common patterns for composer extraction
        composers = [
            'Bach', 'Beethoven', 'Mozart', 'Chopin', 'Brahms', 'Schubert',
            'Schumann', 'Liszt', 'Debussy', 'Ravel', 'Tchaikovsky',
            'Rachmaninoff', 'Prokofiev', 'Shostakovich', 'Stravinsky'
        ]
        
        for composer in composers:
            if composer.lower() in title.lower():
                return composer
                
        return "Unknown"
    
    def _extract_opus(self, title: str) -> Optional[str]:
        """Extract opus number from title"""
        import re
        
        # Look for patterns like "Op. 27", "Op.27", "Op.27 No.2"
        opus_pattern = r'Op\.\s*(\d+(?:\s*No\.\s*\d+)?)'
        match = re.search(opus_pattern, title, re.IGNORECASE)
        
        if match:
            return f"Op. {match.group(1)}"
            
        return None
