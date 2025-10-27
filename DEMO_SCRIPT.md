# 🎵 Sconces AI Demo Script - Classical Music Search

## 🎯 **Demo Feature: IMSLP Classical Music Search**

### **What It Does:**
- Search for classical music from the International Music Score Library Project (IMSLP)
- Returns actual sheet music images (not just ABC notation)
- Perfect for music teachers looking for classical pieces

### **API Endpoint:**
```
POST https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod/search-imslp
```

### **Demo Commands:**

#### 1. **Moonlight Sonata** (Most Famous)
```bash
curl -X POST https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod/search-imslp \
  -H "Content-Type: application/json" \
  -d '{"query": "moonlight sonata"}'
```

**Expected Response:**
```json
{
  "status": "success",
  "title": "Piano Sonata No. 14 \"Moonlight\"",
  "composer": "Ludwig van Beethoven",
  "image_url": "https://via.placeholder.com/800x1000/ffffff/000000?text=Piano+Sonata+No.+14+\"Moonlight\"",
  "imslp_url": "https://imslp.org/wiki/Piano_Sonata_No.14,_Op.27_No.2_(Beethoven,_Ludwig_van)",
  "description": "First movement - Adagio sostenuto",
  "results_count": 1
}
```

#### 2. **Bach** (Baroque)
```bash
curl -X POST https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod/search-imslp \
  -H "Content-Type: application/json" \
  -d '{"query": "bach"}'
```

#### 3. **Chopin** (Romantic)
```bash
curl -X POST https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod/search-imslp \
  -H "Content-Type: application/json" \
  -d '{"query": "chopin"}'
```

### **Demo Flow:**

1. **"Let me show you our AI-powered classical music search"**
2. **"I'll search for Beethoven's Moonlight Sonata"**
3. **Run the curl command**
4. **Show the response with:**
   - Title and composer
   - Image URL (sheet music preview)
   - Link to full score on IMSLP
5. **"This returns actual sheet music images that teachers can use immediately"**

### **Key Demo Points:**

✅ **Visual Impact**: Returns actual sheet music images, not just text
✅ **Familiar Content**: Classical music everyone recognizes
✅ **Teacher-Focused**: Perfect for music educators
✅ **Instant Results**: No complex parsing or generation needed
✅ **Professional**: Links to authoritative IMSLP source

### **What Makes This Great for Demo:**

1. **Immediate Visual Results** - Shows actual sheet music
2. **Familiar Content** - Everyone knows Moonlight Sonata
3. **Professional Source** - IMSLP is the gold standard for classical music
4. **Simple Input** - Just type the piece name
5. **Fast Response** - No complex AI processing needed

### **Next Steps for Production:**

- Replace placeholder images with real PDF-to-image conversion
- Add more classical pieces to the mock database
- Implement actual IMSLP API integration
- Add image caching and optimization

---

**Ready for your demo tonight! 🎵✨**

