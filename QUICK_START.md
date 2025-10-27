# Quick Start Guide - Test Your RAG Pipeline

## 1. Add Your OpenAI API Key

```bash
cd /Users/miriam/Desktop/messageAI

# Create .env file and add your key
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env

# Make sure it's in .gitignore (it should be already)
grep -q "^.env$" .gitignore || echo ".env" >> .gitignore
```

## 2. Test the RAG Pipeline

### Option A: Mock Test (Controlled - Recommended First)
```bash
# Load environment variables
export $(cat .env | xargs)

# Run mock reconciliation (3 simulated tabs)
python3 poc_reconciliation_mock.py
```

**Expected output:**
- 3 tab variations loaded
- GPT-4 analyzes and reconciles them
- Valid ABC notation generated
- Confidence score displayed

### Option B: Real Tab Scraping
```bash
# Load environment variables
export $(cat .env | xargs)

# Run real Ultimate Guitar scraping
python3 poc_reconciliation.py
```

**Expected output:**
- Fetches real tabs from Ultimate Guitar
- Extracts content (85KB+ pages)
- GPT-4 reconciles into ABC notation
- Source URLs displayed

## 3. View Results

Both scripts will show:
- ✅ Fetched tabs (source URLs)
- ✅ ABC notation output
- ✅ Confidence score
- ✅ Validation status

Example ABC output:
```
X:1
T:Baby Shark
M:4/4
L:1/4
K:C
"C"C C C C | "F"F F F F | "G"G G G G | "C"c4 |
```

## 4. What This Proves

✅ **RAG Pipeline Works:**
- Retrieves external guitar tabs
- Augments GPT-4 with retrieved content
- Generates accurate ABC notation

✅ **Ready for Production:**
- Can deploy to AWS Lambda
- Integrate with iOS app
- Render with abcjs in WKWebView

## Troubleshooting

**"No OpenAI API key"**
- Check your .env file: `cat .env`
- Make sure it's loaded: `echo $OPENAI_API_KEY`

**"Could not extract tab content"**
- Some URLs may be chord-only pages (different format)
- This is expected - 1/3 sources working is enough for MVP

**"Invalid ABC notation"**
- GPT-4 may need prompt tuning
- Try running again (stochastic)
- Check validation errors in output

## Next Steps

After successful POC testing:
1. Read `POC_RESULTS.md` for detailed findings
2. Review `RAG_ARCHITECTURE.md` for technical details
3. Start Lambda implementation from `sconces_tasks.md`

---

Need help? Check:
- `ENV_SETUP.md` - Environment configuration
- `POC_RESULTS.md` - Detailed POC findings
- `RAG_ARCHITECTURE.md` - Technical architecture
