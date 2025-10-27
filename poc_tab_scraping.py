#!/usr/bin/env python3
"""
POC: Tab Scraping for Sconces
Tests ability to search and extract guitar tabs from the web
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List, Dict

# You'll need to get a Brave Search API key from: https://brave.com/search/api/
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY', 'YOUR_API_KEY_HERE')

def search_tabs_brave(song_name: str, num_results: int = 5) -> List[Dict]:
    """Search for guitar tabs using Brave Search API"""
    
    if BRAVE_API_KEY == 'YOUR_API_KEY_HERE':
        print("⚠️  Warning: BRAVE_API_KEY not set. Using mock results.")
        return search_tabs_fallback(song_name, num_results)
    
    print(f"\n🔍 Searching Brave for: '{song_name} guitar tab'")
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    
    queries = [
        f"{song_name} guitar tab",
        f"{song_name} chords",
        f"{song_name} ultimate guitar"
    ]
    
    results = []
    
    for query in queries[:1]:  # Just do first query for POC
        params = {
            "q": query,
            "count": num_results
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'web' in data and 'results' in data['web']:
                    for result in data['web']['results']:
                        results.append({
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'description': result.get('description', '')
                        })
                        print(f"  ✓ Found: {result.get('title', 'Untitled')}")
            else:
                print(f"  ✗ Brave API returned status {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error searching: {e}")
    
    return results[:num_results]


def search_tabs_fallback(song_name: str, num_results: int = 5) -> List[Dict]:
    """Fallback: Use regular Google/DuckDuckGo search (for testing without API key)"""
    
    print(f"\n🔍 Searching DuckDuckGo for: '{song_name} guitar tab'")
    
    # DuckDuckGo HTML search (no API key needed)
    url = "https://html.duckduckgo.com/html/"
    data = {
        'q': f'{song_name} guitar tab site:ultimate-guitar.com OR site:songsterr.com OR site:tabs.ultimate-guitar.com'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('a', class_='result__a', limit=num_results):
                title = result.get_text(strip=True)
                href = result.get('href', '')
                
                # DuckDuckGo wraps URLs, extract the actual URL
                if 'uddg=' in href:
                    actual_url = href.split('uddg=')[1].split('&')[0]
                    from urllib.parse import unquote
                    actual_url = unquote(actual_url)
                else:
                    actual_url = href
                
                results.append({
                    'title': title,
                    'url': actual_url,
                    'description': ''
                })
                print(f"  ✓ Found: {title}")
            
            return results
            
    except Exception as e:
        print(f"  ✗ Error searching: {e}")
    
    # If all else fails, return hardcoded test URLs
    print("\n⚠️  Using hardcoded test URLs for Baby Shark")
    return [
        {
            'title': 'Baby Shark - Ultimate Guitar',
            'url': 'https://tabs.ultimate-guitar.com/tab/pinkfong/baby-shark-chords-2555770',
            'description': 'Baby Shark chords'
        }
    ]


def extract_ultimate_guitar_json(html_content: str) -> str:
    """Extract tab content from Ultimate Guitar's JSON data store"""
    import re
    import json
    import html as html_module
    
    # Find the js-store div with data-content
    pattern = r'<div class="js-store" data-content="([^"]+)"'
    match = re.search(pattern, html_content)
    
    if not match:
        return None
    
    # Get HTML-encoded JSON and decode it
    encoded_json = match.group(1)
    decoded_json = html_module.unescape(encoded_json)
    
    try:
        # Parse JSON
        data = json.loads(decoded_json)
        
        # Navigate to tab content
        if 'store' in data and 'page' in data['store']:
            page_data = data['store']['page']
            if 'data' in page_data and 'tab_view' in page_data['data']:
                tab_view = page_data['data']['tab_view']
                
                # Extract the actual tab content
                if 'wiki_tab' in tab_view and 'content' in tab_view['wiki_tab']:
                    return tab_view['wiki_tab']['content']
                
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON decode error: {e}")
        return None
    
    return None


def fetch_with_curl(url: str) -> str:
    """Fetch URL using system curl command (bypasses anti-bot detection)"""
    import subprocess
    
    curl_command = [
        'curl',
        '-s',  # Silent mode
        '-L',  # Follow redirects
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        '-H', 'Accept-Language: en-US,en;q=0.9',
        '--compressed',  # Handle gzip/deflate
        url
    ]
    
    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"  ✗ curl failed with code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ curl timeout after 15 seconds")
        return None
    except Exception as e:
        print(f"  ✗ curl error: {e}")
        return None


def extract_tab_content(url: str) -> Dict:
    """Extract tab content from a URL"""
    
    print(f"\n📄 Fetching content from: {url}")
    
    # Use curl instead of requests to bypass anti-bot detection
    print(f"  Using system curl command...")
    html_content = fetch_with_curl(url)
    
    if not html_content:
        return {'error': 'Failed to fetch content'}
    
    print(f"  ✓ Fetched {len(html_content)} bytes")
    
    content = None
    
    # Try Ultimate Guitar JSON extraction first
    if 'ultimate-guitar.com' in url:
        content = extract_ultimate_guitar_json(html_content)
        if content:
            print(f"  ✓ Extracted from Ultimate Guitar JSON data store")
    
    # Fallback to BeautifulSoup extraction for other sites
    if not content:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try different tab content selectors
        selectors = [
            ('pre', {'class': 'js-tab-content'}),
            ('pre', {'class': 'Htbd7'}),
            ('code', {}),
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                content = element.get_text()
                print(f"  ✓ Found content in <{tag}> with {attrs}")
                break
        
        # Look for any pre tags with tab-like content
        if not content:
            for pre in soup.find_all('pre'):
                text = pre.get_text()
                if any(marker in text for marker in ['Verse', 'Chorus', '[Intro]', '[Verse]', '[Chorus]', 'Capo']):
                    content = text
                    print(f"  ✓ Found tab in pre tag")
                    break
        
        # Look for chord/lyric patterns in divs
        if not content:
            for div in soup.find_all('div'):
                text = div.get_text()
                if len(text) > 100 and any(marker in text for marker in ['Chord', '[Verse]', '[Chorus]', 'Intro:']):
                    content = text
                    print(f"  ✓ Found tab in div")
                    break
    
    if content:
        # Extract first 30 lines for preview
        lines = content.strip().split('\n')
        preview = '\n'.join(lines[:30])
        
        # Try to identify key
        key = extract_key(content)
        
        # Try to identify chords
        chords = extract_chords(content)
        
        return {
            'content': content,
            'preview': preview,
            'line_count': len(lines),
            'detected_key': key,
            'detected_chords': chords[:10] if chords else []
        }
    else:
        print(f"  ✗ Could not extract tab content")
        return {'error': 'Could not extract content'}


def extract_key(content: str) -> str:
    """Try to detect the key from tab content"""
    import re
    
    # Look for "Key: X" or "Capo: X"
    key_match = re.search(r'Key:\s*([A-G][#b]?[m]?)', content, re.IGNORECASE)
    if key_match:
        return key_match.group(1)
    
    # Look for first chord
    chord_match = re.search(r'\[([A-G][#b]?[m]?[0-9]*)\]', content)
    if chord_match:
        return chord_match.group(1)
    
    return 'Unknown'


def extract_chords(content: str) -> List[str]:
    """Extract unique chords from content"""
    import re
    
    # Match chord patterns: [C], [Am], [G7], etc.
    chords = re.findall(r'\[([A-G][#b]?[m]?[0-9]*)\]', content)
    
    # Also try bare chords (common in tabs)
    bare_chords = re.findall(r'\b([A-G][#b]?[m]?[0-9]?)\s+', content)
    
    all_chords = chords + bare_chords
    
    # Remove duplicates, preserve order
    seen = set()
    unique_chords = []
    for chord in all_chords:
        if chord not in seen and len(chord) <= 5:  # Filter out long strings
            seen.add(chord)
            unique_chords.append(chord)
    
    return unique_chords


def print_results(results: List[Dict]):
    """Pretty print the tab extraction results"""
    print("\n" + "="*80)
    print("📊 TAB SCRAPING POC RESULTS")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result #{i} ---")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"URL: {result.get('url', 'N/A')}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Successfully extracted tab")
            print(f"   Lines: {result.get('line_count', 0)}")
            print(f"   Detected Key: {result.get('detected_key', 'Unknown')}")
            print(f"   Detected Chords: {', '.join(result.get('detected_chords', []))}")
            print(f"\n   Preview (first 30 lines):")
            print("   " + "-"*70)
            preview = result.get('preview', '')
            for line in preview.split('\n')[:20]:  # Show first 20 lines
                print(f"   {line}")
            print("   " + "-"*70)


def main():
    print("🎵 Sconces Tab Scraping POC")
    print("="*80)
    
    # Test with Baby Shark
    song_name = input("\nEnter a song name to search (or press Enter for 'Baby Shark'): ").strip()
    if not song_name:
        song_name = "Baby Shark"
    
    print(f"\nTesting with: '{song_name}'")
    
    # Step 1: Search for tabs
    search_results = search_tabs_brave(song_name, num_results=3)
    
    if not search_results:
        print("\n❌ No search results found")
        return
    
    print(f"\n✓ Found {len(search_results)} potential tab sources")
    
    # Step 2: Try to extract content from each result
    tab_results = []
    for i, result in enumerate(search_results[:2], 1):  # Test first 2 results
        print(f"\n--- Testing source {i}/{len(search_results[:2])} ---")
        
        tab_data = extract_tab_content(result['url'])
        tab_data['title'] = result['title']
        tab_data['url'] = result['url']
        
        tab_results.append(tab_data)
    
    # Step 3: Print summary
    print_results(tab_results)
    
    # Analysis
    successful = sum(1 for r in tab_results if 'error' not in r)
    print(f"\n" + "="*80)
    print(f"📈 SUMMARY")
    print(f"="*80)
    print(f"✅ Successfully extracted: {successful}/{len(tab_results)}")
    print(f"❌ Failed: {len(tab_results) - successful}/{len(tab_results)}")
    
    if successful > 0:
        print("\n✨ POC Result: TAB SCRAPING IS FEASIBLE")
        print("\nNext steps:")
        print("  1. Get Brave Search API key (or use alternative search)")
        print("  2. Improve content extraction for different sites")
        print("  3. Implement GPT-4 reconciliation of multiple sources")
    else:
        print("\n⚠️  POC Result: TAB SCRAPING NEEDS MORE WORK")
        print("\nConsiderations:")
        print("  1. Sites may block automated requests")
        print("  2. May need to use Selenium for JavaScript-rendered content")
        print("  3. Consider alternative: user pastes tab content directly")


if __name__ == '__main__':
    main()

