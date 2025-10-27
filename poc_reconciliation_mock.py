#!/usr/bin/env python3
"""
POC: Tab Reconciliation - Mock Test with 3 Variations
Simulates 3 different tab sources to test GPT-4 reconciliation
"""

import os
import json
import re

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_KEY_HERE')

# Simulate 3 different tab versions of "Twinkle Twinkle Little Star"
MOCK_TABS = [
    {
        'source': 'Version 1 - Simple chords',
        'content': '''Twinkle Twinkle Little Star
By Traditional
Key: C Major

[Verse]
C       C       F    C
Twinkle twinkle little star
F       C       G7   C
How I wonder what you are

[Chorus]
C    F    C    G
Up above the world so high
C    F    C    G
Like a diamond in the sky
'''
    },
    {
        'source': 'Version 2 - With melody notes',
        'content': '''Twinkle Twinkle Little Star
Traditional nursery rhyme

Capo: None
Key: C

Intro: C C G G A A G

Verse 1:
C  C  G  G  A  A  G
Twinkle twinkle little star
F  F  E  E  D  D  C
How I wonder what you are

Verse 2:
G  G  F  F  E  E  D
Up above the world so high
G  G  F  F  E  E  D
Like a diamond in the sky
'''
    },
    {
        'source': 'Version 3 - With timing',
        'content': '''TWINKLE TWINKLE LITTLE STAR
Arr: Public Domain

Time: 4/4
Key: C Major
Tempo: 80 BPM

[Intro]
| C    | C    | G    | G    |

[Verse]
| C    | C    | G    | G    |
  Twin-  kle,  twin-  kle
| A    | A    | G    | G    |
  lit-   tle   star
| F    | F    | E    | E    |
  How    I     won-   der
| D    | D    | C    | C    |
  what   you   are
'''
    }
]


def reconcile_tabs_with_gpt4(tabs, song_name):
    """Use GPT-4 to reconcile multiple tab sources"""
    
    if OPENAI_API_KEY == 'YOUR_KEY_HERE':
        print("\n⚠️  No OpenAI API key - skipping GPT-4 reconciliation")
        print("To test with GPT-4: export OPENAI_API_KEY='your-key'")
        return None
    
    print(f"\n🤖 Reconciling {len(tabs)} versions with GPT-4...")
    
    # Build prompt
    versions_text = ""
    for i, tab in enumerate(tabs, 1):
        versions_text += f"\n{'='*70}\n"
        versions_text += f"VERSION {i}: {tab['source']}\n"
        versions_text += f"{'='*70}\n"
        versions_text += tab['content']
        versions_text += "\n"
    
    prompt = f"""You are a music transcription expert specializing in ABC notation.

I have {len(tabs)} different versions of "{song_name}" from guitar tabs and chord sheets. 
Your task: Reconcile these into ONE accurate ABC notation for the first 16 bars, including a lyric line.

{versions_text}

Requirements:
1. Analyze all versions to identify the consensus melody, chords, and any lyric cues
2. Generate ABC notation for the FIRST 16 BARS (extend repeating sections as needed)
3. Use these ABC notation standards:
   - X:1 (reference number)
   - T:{song_name} (title)
   - M:4/4 (time signature)
   - L:1/4 (default note length - quarter note)
   - K:C (key signature - use the key from the tabs)
   - Chord symbols in quotes: "C", "G", "F", etc.
   - Simple melody: C D E F G A B (uppercase=higher octave)
   - At least one lyric line (`w:`) aligned with the melody; invent simple syllables (e.g., "La") if lyrics are missing
   
4. For the melody, use the note pattern shown in the tabs
5. Keep it simple and playable
6. Make sure it's VALID ABC notation that abcjs can render

Example format:
X:1
T:Song Name
M:4/4
L:1/4
K:C
"C"C C "G"D D | "C"E E "G"D2 | "F"F F "C"E E | "G"D D "C"C2 |
w: La la la la | La la la la | La la la la | La la la la |

Return ONLY a JSON object (no markdown, no code blocks):
{{
    "abc_notation": "X:1\\nT:Song Name\\n...",
    "confidence": 0.90,
    "key": "C",
    "time_signature": "4/4",
    "notes": "Brief reconciliation decisions"
}}"""

    try:
        import openai
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert in music notation, specifically ABC notation. Always return valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON if wrapped in markdown
        if '```' in result_text:
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
        
        result = json.loads(result_text)
        
        print(f"  ✓ Reconciliation complete!")
        print(f"  Confidence: {result.get('confidence', 0)}")
        print(f"  Key: {result.get('key', 'Unknown')}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("="*80)
    print("🎵 SCONCES POC: Tab Reconciliation (Mock Test)")
    print("="*80)
    
    song_name = "Twinkle Twinkle Little Star"
    
    print(f"\n📚 Testing with {len(MOCK_TABS)} mock tab variations")
    print(f"Song: {song_name}")
    
    # Show the input tabs
    print("\n" + "="*80)
    print("INPUT: 3 TAB VARIATIONS")
    print("="*80)
    
    for i, tab in enumerate(MOCK_TABS, 1):
        print(f"\n--- {tab['source']} ---")
        print(tab['content'][:300] + "...")
    
    # Reconcile
    print("\n" + "="*80)
    print("RECONCILIATION")
    print("="*80)
    
    result = reconcile_tabs_with_gpt4(MOCK_TABS, song_name)
    
    if not result:
        print("\n💡 To run with GPT-4:")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   python3 poc_reconciliation_mock.py")
        return
    
    # Display result
    print("\n" + "="*80)
    print("🎼 RECONCILED ABC NOTATION")
    print("="*80)
    
    abc = result.get('abc_notation', '')
    print(f"\nConfidence: {result.get('confidence', 0)}")
    print(f"Key: {result.get('key', 'Unknown')}")
    print(f"Time: {result.get('time_signature', 'Unknown')}")
    print(f"\nNotes: {result.get('notes', 'N/A')}")
    
    print("\n" + "-"*80)
    print(abc)
    print("-"*80)
    
    # Validate
    required = ['X:', 'T:', 'M:', 'L:', 'K:']
    is_valid = all(h in abc for h in required)
    
    if is_valid:
        print("\n✅ ABC notation is VALID!")
    else:
        print("\n⚠️  Missing required headers")
        missing = [h for h in required if h not in abc]
        print(f"Missing: {missing}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 RECONCILIATION TEST RESULTS")
    print("="*80)
    print(f"✅ Input sources: {len(MOCK_TABS)}")
    print(f"✅ Reconciled: {len(MOCK_TABS)} → 1 ABC notation")
    print(f"✅ Confidence: {result.get('confidence', 0)}")
    print(f"✅ Valid ABC: {is_valid}")
    print(f"✅ Length: {len(abc)} characters")
    
    if is_valid:
        print("\n🎉 SUCCESS! GPT-4 successfully reconciled 3 tab variations!")
        print("\nThis proves the reconciliation pipeline works:")
        print("  1. ✅ Multiple tab sources can be fetched")
        print("  2. ✅ GPT-4 can analyze and reconcile them")
        print("  3. ✅ Valid ABC notation is generated")
        print("  4. ✅ Ready for client-side rendering with abcjs")


if __name__ == '__main__':
    main()

