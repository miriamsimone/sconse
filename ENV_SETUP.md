# Environment Setup for Sconces POC

## Quick Start

1. **Create your .env file:**
```bash
cd /Users/miriam/Desktop/messageAI
touch .env
```

2. **Add your OpenAI API key:**
```bash
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

3. **Test the POC scripts:**
```bash
# Load environment
export $(cat .env | xargs)

# Test mock reconciliation (controlled test)
python3 poc_reconciliation_mock.py

# Test real Ultimate Guitar scraping + reconciliation
python3 poc_reconciliation.py
```

## Environment Variables

### Required for POC:
- `OPENAI_API_KEY` - Your OpenAI API key (get from https://platform.openai.com/api-keys)

### Optional:
- `BRAVE_API_KEY` - Brave Search API key (free tier: 2,000/month)

## Testing the POC

Once your API key is set, run:

```bash
# Option 1: Test with mock data (3 simulated tab variations)
python3 poc_reconciliation_mock.py

# Option 2: Test with real Ultimate Guitar scraping
python3 poc_reconciliation.py
```

Both scripts will:
1. Retrieve tab/chord information
2. Send to GPT-4 for reconciliation
3. Generate valid ABC notation
4. Display results with validation
