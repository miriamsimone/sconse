#!/usr/bin/env python3
"""
POC: Tab Reconciliation with GPT-4
Tests retrieving 3 different tabs and using GPT-4 to reconcile them into ABC notation
"""

import subprocess
import re
import json
import html as html_module
import os
from typing import List, Dict

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_KEY_HERE')


def fetch_with_curl(url: str) -> str:
    """Fetch URL using system curl command"""
    curl_command = [
        'curl', '-s', '-L',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        '--compressed',
        url
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=15)
        return result.stdout if result.returncode == 0 else None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_ultimate_guitar_json(html_content: str) -> str:
    """Extract tab content from Ultimate Guitar's JSON data store"""
    pattern = r'<div class="js-store" data-content="([^"]+)"'
    match = re.search(pattern, html_content)
    
    if not match:
        return None
    
    encoded_json = match.group(1)
    decoded_json = html_module.unescape(encoded_json)
    
    try:
        data = json.loads(decoded_json)
        
        if 'store' in data and 'page' in data['store']:
            page_data = data['store']['page']
            if 'data' in page_data and 'tab_view' in page_data['data']:
                tab_view = page_data['data']['tab_view']
                
                if 'wiki_tab' in tab_view and 'content' in tab_view['wiki_tab']:
                    return tab_view['wiki_tab']['content']
    except:
        pass
    
    return None


def search_ultimate_guitar_tabs(song_name: str) -> List[str]:
    """Search for multiple Ultimate Guitar tabs for a song"""
    
    print(f"\n🔍 Searching for Ultimate Guitar tabs: '{song_name}'")
    
    # For POC, using known Baby Shark URLs from Ultimate Guitar
    # In production, you'd use Brave Search API with site:tabs.ultimate-guitar.com
    
    baby_shark_urls = [
        "https://tabs.ultimate-guitar.com/tab/misc-children/pinkfong-baby-shark-tabs-2223681",
        "https://tabs.ultimate-guitar.com/tab/misc-children/baby-shark-chords-2555770",
        "https://tabs.ultimate-guitar.com/tab/pinkfong/baby-shark-chords-2574890"
    ]
    
    twinkle_urls = [
        "https://tabs.ultimate-guitar.com/tab/misc-traditional/twinkle-twinkle-little-star-chords-800415",
        "https://tabs.ultimate-guitar.com/tab/traditional/twinkle-twinkle-little-star-chords-1123456",
        "https://tabs.ultimate-guitar.com/tab/nursery-rhymes/twinkle-twinkle-little-star-tabs-1234567"
    ]
    
    if 'baby shark' in song_name.lower():
        return baby_shark_urls
    elif 'twinkle' in song_name.lower():
        print("  (Note: Using Baby Shark URLs for demo - Twinkle URLs may not exist)")
        return baby_shark_urls[:1]  # Just use one for now
    else:
        return baby_shark_urls


def fetch_tabs(urls: List[str]) -> List[Dict]:
    """Fetch tab content from multiple URLs"""
    
    tabs = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n📄 Fetching source {i}/{len(urls)}: {url}")
        
        html_content = fetch_with_curl(url)
        
        if not html_content:
            print(f"  ✗ Failed to fetch")
            continue
        
        print(f"  ✓ Fetched {len(html_content):,} bytes")
        
        tab_content = extract_ultimate_guitar_json(html_content)
        
        if tab_content:
            lines = len(tab_content.split('\n'))
            print(f"  ✓ Extracted tab ({lines} lines)")
            
            # Get first 40 lines as a preview
            preview = '\n'.join(tab_content.split('\n')[:40])
            
            tabs.append({
                'url': url,
                'content': tab_content,
                'preview': preview,
                'lines': lines
            })
        else:
            print(f"  ✗ Could not extract tab content")
    
    return tabs


def reconcile_tabs_with_gpt4(tabs: List[Dict], song_name: str) -> Dict:
    """Use GPT-4 to reconcile multiple tab sources into ABC notation"""
    
    if OPENAI_API_KEY == 'YOUR_KEY_HERE':
        print("\n⚠️  No OpenAI API key set - returning mock reconciliation")
        return {
            'abc_notation': mock_abc_notation(song_name),
            'confidence': 0.75,
            'notes': 'Mock reconciliation (no API key provided)'
        }
    
    print(f"\n🤖 Reconciling {len(tabs)} tabs with GPT-4...")
    
    # Prepare the prompt
    versions_text = ""
    for i, tab in enumerate(tabs, 1):
        versions_text += f"\n--- VERSION {i} (from {tab['url']}) ---\n"
        versions_text += tab['preview']
        versions_text += "\n" + "="*80 + "\n"
    
    prompt = f"""You are a music transcription expert. You have {len(tabs)} different guitar tab versions of "{song_name}".

Your task is to reconcile them into a single, accurate version in ABC notation format.

{versions_text}

Instructions:
1. Analyze all versions and identify the most reliable chord progressions, melody, and any lyric cues
2. Extract the first 16 bars (measures), extending repeating patterns if needed to cover 16 bars
3. Identify the key signature from the tabs
4. Create ABC notation with:
   - Standard ABC headers (X, T, M, L, K)
   - Chord symbols above the staff (use "C", "G", "Am" format)
   - Simple melody line (quarter notes and half notes)
   - A lyric line using `w:` that aligns syllables to the melody (invent simple syllables like "La" when lyrics are missing)
   - Keep it playable and accurate

5. Output VALID ABC notation format that can be rendered by abcjs

Return ONLY a JSON object with this structure (no markdown, no code blocks):
{{ 
    "abc_notation": "X:1\\nT:{song_name}\\nM:4/4\\nL:1/4\\nK:C\\n\\"C\\"C D E F | \\"G\\"G2 A2 | ...\\nw: La la la la | ...",
    "confidence": 0.85,
    "key": "C",
    "notes": "Brief explanation of reconciliation decisions"
}}"""

    try:
        import openai
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a music notation expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON (sometimes GPT wraps it in markdown)
        if '```' in result_text:
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
        
        result = json.loads(result_text)
        
        print(f"  ✓ Reconciliation complete (confidence: {result.get('confidence', 0)})")
        
        return result
        
    except Exception as e:
        print(f"  ✗ Error during reconciliation: {e}")
        return {
            'abc_notation': mock_abc_notation(song_name),
            'confidence': 0.5,
            'notes': f'Fallback due to error: {str(e)}'
        }


def mock_abc_notation(song_name: str) -> str:
    """Generate mock ABC notation for testing without API key"""
    return f"""X:1
T:{song_name}
M:4/4
L:1/4
K:C
"C"C D E F | "G"G2 A2 | "Am"A G F E | "F"F4 |"""


def validate_abc(abc_notation: str) -> bool:
    """Validate ABC notation has required headers"""
    required = ['X:', 'T:', 'M:', 'L:', 'K:']
    return all(header in abc_notation for header in required)


def main():
    print("="*80)
    print("🎵 SCONCES POC: Tab Reconciliation with GPT-4")
    print("="*80)
    
    # Get song name
    song_name = input("\nEnter song name (or press Enter for 'Baby Shark'): ").strip()
    if not song_name:
        song_name = "Baby Shark"
    
    print(f"\n🎸 Testing reconciliation for: '{song_name}'")
    
    # Step 1: Find tab URLs (in production, use Brave Search)
    urls = search_ultimate_guitar_tabs(song_name)
    print(f"\n✓ Found {len(urls)} potential sources")
    
    # Step 2: Fetch tabs
    print("\n" + "="*80)
    print("STEP 1: FETCHING TABS")
    print("="*80)
    
    tabs = fetch_tabs(urls)
    
    if not tabs:
        print("\n❌ No tabs successfully fetched!")
        return
    
    print(f"\n✅ Successfully fetched {len(tabs)} tabs")
    
    # Display previews
    print("\n" + "="*80)
    print("TAB PREVIEWS")
    print("="*80)
    
    for i, tab in enumerate(tabs, 1):
        print(f"\n--- SOURCE {i} ({tab['lines']} lines total) ---")
        print(tab['preview'][:500])  # First 500 chars
        print("...")
    
    # Step 3: Reconcile with GPT-4
    print("\n" + "="*80)
    print("STEP 2: RECONCILING WITH GPT-4")
    print("="*80)
    
    result = reconcile_tabs_with_gpt4(tabs, song_name)
    
    # Display results
    print("\n" + "="*80)
    print("🎼 RECONCILIATION RESULT")
    print("="*80)
    
    print(f"\nConfidence: {result.get('confidence', 0)}")
    print(f"Key: {result.get('key', 'Unknown')}")
    print(f"Notes: {result.get('notes', 'N/A')}")
    
    print("\n📝 ABC Notation:")
    print("-"*80)
    abc = result.get('abc_notation', '')
    print(abc)
    print("-"*80)
    
    # Validate
    if validate_abc(abc):
        print("\n✅ ABC notation is valid!")
    else:
        print("\n⚠️  ABC notation may be missing required headers")
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"✅ Fetched: {len(tabs)} tab sources")
    print(f"✅ Reconciled: {len(tabs)} → 1 ABC notation")
    print(f"✅ Confidence: {result.get('confidence', 0)}")
    print(f"✅ ABC Length: {len(abc)} characters")
    
    if validate_abc(abc):
        print("\n✨ POC SUCCESS! Ready for iOS rendering with abcjs")
        print("\nNext steps:")
        print("  1. Deploy this logic to AWS Lambda")
        print("  2. Add Brave Search API for dynamic URL discovery")
        print("  3. Add transposition logic")
        print("  4. Integrate with iOS app + WKWebView + abcjs")
    else:
        print("\n⚠️  ABC validation failed - may need prompt tuning")


if __name__ == '__main__':
    main()

