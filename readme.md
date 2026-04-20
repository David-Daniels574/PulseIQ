# **ByteForge NLP Project - Comprehensive Technical Documentation**

## **1. Project Overview**

**Project Name**: ByteForge Aspect-Based Sentiment Analysis (ABSA) System  
**Domain**: Food & Beverage (F&B) Industry Intelligence Platform  
**Primary Function**: Multi-source sentiment analysis, aspect extraction, and business intelligence generation for restaurants, cafes, and bars  
**Tech Stack**: Python FastAPI backend, React/Next.js frontend, ChromaDB vector store, Google Gemini LLM  
**Production Sentiment Model**: RoBERTa fine-tuned on Yelp reviews (50K samples)

---

## **2. NLP Architecture & Core Components**

### **2.1 Sentiment Analysis Pipeline (Production Model)**

#### **Fine-Tuned Sentiment Model**

**Base Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Architecture**: RoBERTa-base pre-trained on Twitter data
- **Fine-tuning Dataset**: Yelp Review Full (50,000 training samples, 5,000 test samples)
- **Framework**: Hugging Face Transformers
- **Production Model Path**: `./models/pulseiq_finetuned_model`

**Fine-tuning Configuration**:
```
Training Data:
  - Source: Yelp Review Full (kaggle dataset)
  - Train: 50,000 reviews
  - Test: 5,000 reviews
  - Label Mapping (5-star → 3-class):
    * Stars 1-2 → Negative (label 0)
    * Star 3 → Neutral (label 1)
    * Stars 4-5 → Positive (label 2)

Hyperparameters:
  - Learning rate: 2e-5
  - Batch size: 32 (distributed x2 T4 GPUs via fp16)
  - Epochs: 3
  - Optimizer: AdamW with weight decay 0.01
  - Mixed precision: fp16 enabled (GPU optimization)
  - Max sequence length: 256 tokens
  - Evaluation strategy: Per-epoch
```

**Why Yelp Fine-tuning?**
1. **Domain Alignment**: Yelp reviews are restaurant/service reviews → perfect transfer learning target for F&B ABSA
2. **Label Distribution**: 5-star scale naturally maps to 3-class sentiment hierarchy (Positive/Neutral/Negative) used in ABSA framework
3. **Data Scale**: 50K training samples sufficient for robust fine-tuning without overfitting on specialized domain
4. **Vocabulary Transfer**: RoBERTa pre-trained on Twitter → further adapted to restaurant-specific language via Yelp

**Expected Improvements Over Base Model**:
- More accurate restaurant/F&B-specific sentiment vocabulary
- Better handling of colloquial restaurant language (e.g., "soggy crust", "amazing ambiance", "cozy vibe")
- Higher confidence calibration for aspect-specific sentiments
- Reduced false positives on sarcasm (Yelp data rich in mixed sentiments)

**Model Loading** (analyzer.py):
```python
# Production: Use Yelp fine-tuned model
MODEL_NAME = os.getenv("PULSEIQ_MODEL_PATH", "./models/pulseiq_finetuned_model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    top_k=None  # Get all class scores for confidence extraction
)
```

**Supported Outputs**: `["Negative", "Neutral", "Positive"]`  
**Confidence Scores**: Top-k probability across all 3 labels

### **2.2 Aspect-Based Sentiment Analysis (ABSA) System**

#### **Aspect Detection Strategy**
**Approach**: Keyword-based aspect detection with category-aware lexicons

**Aspect Categories by Business Type**:

1. **Restaurant Aspects**:
   - Food (taste, quality, portion, freshness)
   - Service (staff, speed, attentiveness, professionalism)
   - Ambiance (decor, noise, cleanliness, comfort)
   - Price (value, cost, affordability)

2. **Cafe Aspects**:
   - Drinks & Coffee (quality, strength, flavor)
   - Food & Pastries (freshness, variety)
   - Service (barista quality, speed)
   - Workspace & Ambiance (wifi, noise, seating)
   - Price (value for money)

3. **Bar Aspects**:
   - Drinks & Alcohol (quality, variety, pour size)
   - Food & Snacks (menu quality, portion)
   - Service (bartender skill, attentiveness)
   - Vibe & Crowd (music, atmosphere, cleanliness)
   - Price & Cover (entry cost, value)

#### **Keyword Matching Algorithm** (analyzer.py):
```python
def analyze_review_for_aspects(review_text: str):
    1. Sentence tokenization using NLTK punkt tokenizer
    2. For each sentence:
       - Lowercase conversion
       - Keyword matching against ASPECT_KEYWORDS dict
       - Multi-keyword matching (any keyword triggers aspect detection)
    3. For matching sentences:
       - Sentiment analysis via fine-tuned RoBERTa pipeline
       - Confidence score extraction from model probabilities
       - Sentence preservation for citation/evidence
    4. Aggregation: Group by aspect with sentiments + confidence scores
```

#### **Category Detection**
- **Function**: `detect_business_category()` 
- **Aliases-based matching**: restaurant → [diner, eatery, bistro, grill, steakhouse]
- **Fallback**: DEFAULT_ASPECT_KEYWORDS if category not recognized
- **Dynamic Loading**: `set_aspect_keywords_for_category()` loads F&B-specific keywords at runtime

### **2.3 Text Processing & Tokenization**

**Libraries Used**:
- **NLTK** (v3.9.1):
  - `punkt` tokenizer for sentence segmentation
  - Automatic NLTK data download on first use
  
- **Transformers Tokenizer** (from fine-tuned model):
  - RoBERTa BPE tokenizer for subword tokenization
  - Handles OOV (out-of-vocabulary) words via byte-pair encoding
  - Max length: 256 tokens (optimized for typical review sentences)
  
- **Custom Tokenization**:
  - Alphanumeric extraction with whitespace normalization
  - Used in SWOT/PESTEL keyword matching for robustness

---

## **3. Multi-Source Data Integration**

### **3.1 Review Sources**

| Source | Method | NLP Integration | File |
|--------|--------|-----------------|------|
| **Google Maps** | Maps API (googlemaps library) | Direct review ingestion → ABSA | main.py |
| **Twitter/X** | RapidAPI Twitter241 | Tweet fetching + NLI filtering | twitter_scraper.py |
| **News Articles** | Google News RSS + HTML scraping | Headline analysis + PESTEL categorization | scraper.py |

### **3.2 Twitter Review Filtering (NLI-based)**

**Model**: `cross-encoder/nli-MiniLM2-L6-H768` (CrossEncoder)

**Pipeline** (twitter_scraper.py):
```
1. Fetch tweets using RapidAPI
2. Regex pre-filter: Remove non-review tweets
   - Exclude: "RT ", "hiring", "giveaway", "contest", etc.
   - Minimum 5 tokens requirement
3. Hypothesis: "I am sharing my opinion about the food and my 
               experience eating at this restaurant."
4. NLI Classification:
   - Entailment (0.55+ threshold) = valid review
   - Returns list of {text, confidence_score}
5. Batch inference: All tweets in single model call for efficiency
```

**Key Insight**: Uses NLI as a review authenticity filter rather than sentiment classifier

---

## **4. Advanced Confidence & Multi-Source Scoring**

### **4.1 Confidence Engine** (confidence_engine.py)

**Compound Confidence Formula**:
```
confidence_score(aspect) = 
    SOURCE_WEIGHT × (0.3 × RECENCY_WEIGHT + 0.4 × VOLUME_WEIGHT + 
                     0.2 × SENTIMENT_STRENGTH + 0.1 × AGREEMENT_BONUS) 
    × CONFLICT_PENALTY
```

**Components**:

1. **Source Base Weights**:
   - Google Maps: 0.90 (highest credibility)
   - Twitter: 0.80 (medium credibility)
   - News: 0.65 (contextual credibility)

2. **Recency Weight** (0.5 → 1.0 decay):
   - Last 30 days: 1.0
   - Linear decay over 6 months
   - Minimum floor: 0.5

3. **Volume Weight** (logarithmic):
   - Formula: `min(1.0, 0.4 + 0.3 × log₁₀(mention_count + 1))`
   - 1 mention → 0.4, 5 → 0.65, 10+ → 0.75

4. **Agreement Bonus** (cross-source consensus):
   - 2 agreeing sources: +7%
   - 3 agreeing sources: +12%
   - All 3 sources: +15%

5. **Conflict Detection**:
   - Flag when Positive and Negative sentiments across sources
   - -10% confidence penalty on conflicts
   - Returns `(conflict_flag, conflict_detail)`

### **4.2 Sentiment Variance Analysis**

**Purpose**: Identify inconsistent customer experiences

**Calculation**:
```python
variance = calculate_aspect_variance(aspect_sentiments)
- Uses numpy.std() on confidence scores per aspect
- Clusters complaints via DBSCAN for MECE analysis
- Flags high-variance aspects (>0.3) as operational issues
```

---

## **5. Embedding & RAG System**

### **5.1 Vector Store Architecture** (llm_insights.py)

**Technology**: ChromaDB (Persistent Vector Database)

**Custom Embedding Function**:
```python
class GeminiEmbeddingFunction(chromadb.EmbeddingFunction):
    - Uses Google Gemini API: models/text-embedding-004
    - Task type: RETRIEVAL_DOCUMENT (optimized for semantic search)
    - Batch processing for efficiency
```

**Ingestion Pipeline**:
```python
ingest_reviews_to_chroma(business_name, review_texts):
    1. Create collection: f"reviews_{business_name_normalized}"
    2. Generate unique review IDs
    3. Upsert (update/insert) documents + embeddings
    4. Persistent storage at ./chroma_db/
```

### **5.2 RAG (Retrieval-Augmented Generation)**

**Retrieval Function**: `retrieve_rag_context()`

```
Process:
1. Extract ABSA results → identify non-Neutral aspects
2. Generate query texts:
   - Format: "{SENTIMENT} customer feedback about {ASPECT}"
   - Only strong opinions (skip Neutral)
3. Chroma semantic search:
   - Query embedding via Gemini
   - Find top-3 most similar reviews
   - Deduplicate results
4. Format as prompt context for LLM
```

**Use Case**: Inject real review examples into Gemini prompts for grounded insights

---

## **6. Large Language Model Integration**

### **6.1 Gemini LLM Configuration**

**Model**: `models/gemini-2.5-flash`  
**API Provider**: Google Generative AI  
**Key Features**:
- Low-latency inference
- Structured JSON output with validation
- Token-efficient for streaming insights

**Key Files**:
- llm_insights.py - Insight generation
- framework_llm.py - Strategic frameworks
- agentic_swot.py - SWOT analysis
- agentic_pestel.py - PESTEL analysis
- agentic_mece.py - MECE clustering

### **6.2 Business Insights Generation** (llm_insights.py)

**Prompt Engineering**:
```
Input to Gemini:
1. Analysis summary (ABSA results + business info)
2. RAG-retrieved review snippets (from ChromaDB)
3. Cross-source confidence scores
4. Sentiment variances + conflict flags
5. Fine-tuned RoBERTa sentiment outputs

Output:
- Strategic recommendations (JSON)
- Prioritized action items
- Root cause analysis
- Quick summary (under 150 words)
```

### **6.3 Review Response Templates**

**Function**: `generate_review_response_template()`

```python
Inputs:
- Aspect (Food, Service, Ambiance, Price)
- Sentiment (Positive, Negative, Neutral)
- Business name

Output:
- Personalized owner response template
- Tone: Professional, empathetic, action-oriented
```

---

## **7. Strategic Framework Analysis**

### **7.1 Multi-Framework Generation** (framework_llm.py)

**Single API Call → 8 Framework Outputs**:

1. **SWOT Analysis**
   - Strengths: Positive aspects + confidence
   - Weaknesses: Negative aspects + conflict flags
   - Opportunities: Competitor gaps
   - Threats: News mentions + trends

2. **PESTEL Analysis** (keyword-based + LLM-enhanced)
   - Political: Policy/government keywords
   - Economic: Price/cost/inflation keywords
   - Social: Lifestyle/trends keywords
   - Technological: Platform/app/AI keywords
   - Environmental: Sustainability keywords
   - Legal: Compliance/license keywords

3. **BCG Matrix** (menu items classification)
   - Stars: High growth + high market share
   - Cash Cows: High market share, low growth
   - Question Marks: Low market share, high growth
   - Dogs: Low on both dimensions

4. **VRIO Analysis**
   - Valuable: Contributes to competitive advantage
   - Rare: Few competitors possess
   - Inimitable: Difficult to copy
   - Organized: Resources properly coordinated

5. **Ansoff Matrix** (growth strategies)
   - Market Penetration
   - Market Development
   - Product Development
   - Diversification

6. **MECE Clustering** (Mutually Exclusive + Collectively Exhaustive)
   - Pre-clusters complaints
   - Ensures no overlap
   - Comprehensive coverage

7. **Six Sigma** (variance analysis)
   - Defect categorization
   - Root cause identification
   - Corrective actions

8. **4 P's Framework**
   - Product: Menu quality + innovation
   - Price: Value perception + positioning
   - Place: Location + distribution
   - Promotion: Marketing signals from reviews

### **7.2 Framework Prompt Construction** (framework_llm.py)

**Data Injected into Single Mega-Prompt**:
```json
{
  "aggregated_absa": [...],           // Cross-source sentiment
  "competitor_summaries": [...],      // Competitor intelligence
  "menu_items": [...],                // Product data
  "virality_index": {...},            // Social signals
  "news_mentions": [...],             // External context
  "mece_clusters": [...],             // Pre-clustered complaints
  "sentiment_variances": {...},       // Consistency metrics
  "date_range": "..."                 // Analysis period
}
```

**Output Validation**: Strict JSON schema with `EXPECTED_KEYS` for each framework

---

## **8. Predictive Analytics**

### **8.1 Rating Forecasting** (forecasting.py)

**Model Type**: XGBoost Gradient Boosting Machine

**Features**:
- City (categorical, label-encoded)
- Category (categorical, label-encoded)
- Current rating (numerical)
- Sentiment score (numerical) — **Sourced from fine-tuned RoBERTa predictions**

**Custom Handling**:
- `UnseenLabelTransformer` class for robust unseen category handling
- Placeholder: `__UNSEEN_LABEL__` for new cities/categories
- Joblib serialization with module injection for unpickling

**Sentiment Input Pipeline**:
```
Fine-tuned RoBERTa ABSA → Confidence scores per aspect
    ↓
Aggregate confidence scores (weighted by aspect importance)
    ↓
Create sentiment_score feature (0-100 scale)
    ↓
XGBoost model ingests as input feature
    ↓
Rating forecast generation
```

**Prediction Output**:
```python
generate_rating_forecast(city, category, current_rating, sentiment_score, months_ahead=6)
→ Returns: List[Dict] with forecasted ratings for next N months
```

---

## **9. NLP-Specific Dependencies**

### **Core NLP Libraries**

```txt
transformers==4.46.3              # Hugging Face transformer models (RoBERTa)
torch==2.5.1                       # PyTorch (backend for transformers)
nltk==3.9.1                        # Natural Language Toolkit (tokenization)
sentence-transformers==3.3.1       # Sentence embeddings + CrossEncoder (NLI)
google-generativeai==0.8.4         # Gemini API integration
chromadb==0.5.23                   # Vector database (RAG)
langchain==0.3.19                  # LLM orchestration
langchain-core==0.3.40
langchain-google-genai==2.0.9
```

### **ML/Scientific Libraries**
```txt
scikit-learn==1.5.2                # For preprocessing + DBSCAN clustering
xgboost==2.1.3                     # Gradient boosting models (forecasting)
numpy==1.26.4                      # Numerical operations
pandas==2.2.3                      # Data manipulation
scipy==1.14.1                      # Statistical functions
joblib==1.4.2                      # Model serialization (fine-tuned model loading)
```

---

## **10. Data Flow & Processing Pipeline**

### **End-to-End NLP Pipeline**

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: Business Reviews                       │
│         (Google Maps, Twitter, News Headlines)                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              TEXT PREPROCESSING & FILTERING                      │
│  • Sentence tokenization (NLTK)                                 │
│  • NLI filtering for Twitter (CrossEncoder)                     │
│  • Regex cleaning                                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│       CATEGORY DETECTION & ASPECT EXTRACTION                     │
│  • Business type classification (restaurant/cafe/bar)            │
│  • Keyword-based aspect identification                           │
│  • Sentence-to-aspect mapping                                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  SENTIMENT ANALYSIS (Fine-tuned RoBERTa on Yelp 50K samples)    │
│  • Per-sentence sentiment classification                         │
│  • Confidence score extraction                                   │
│  • Label mapping (LABEL_0/1/2 → Negative/Neutral/Positive)      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│       MULTI-SOURCE CONFIDENCE SCORING                            │
│  • Source weighting (Google Maps > Twitter > News)              │
│  • Recency adjustment                                            │
│  • Volume normalization                                          │
│  • Cross-source agreement bonus                                  │
│  • Conflict detection & flagging                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         EMBEDDINGS & RAG INGESTION                               │
│  • Gemini embedding (text-embedding-004)                        │
│  • ChromaDB persistent storage                                   │
│  • Semantic indexing for retrieval                               │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│      LLM-POWERED INSIGHT GENERATION                              │
│  • RAG context retrieval from ChromaDB                           │
│  • Gemini LLM processing (gemini-2.5-flash)                     │
│  • Prompt injection with confidence scores                       │
│  • Strategic recommendations generation                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│       FRAMEWORK ANALYSIS (8 frameworks)                          │
│  • SWOT, PESTEL, BCG, VRIO, Ansoff, MECE, Six Sigma, 4P's       │
│  • Single mega-prompt with all aggregated data                  │
│  • JSON output with confidence per point                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│   PREDICTIVE ANALYTICS (XGBoost + Fine-tuned Sentiment)         │
│  • Rating forecasting for next N months                          │
│  • City/category/RoBERTa-sentiment features                      │
│  • Confidence intervals                                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              OUTPUT: Business Intelligence Dashboard             │
│    (Reviews, Insights, Frameworks, Forecasts)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## **11. Key NLP Methodologies**

### **11.1 Aspect-Based Sentiment Analysis (ABSA)**

**Approach**: Supervised keyword-lexicon hybrid with fine-tuned sentiment model
- Keywords identify aspect candidates (domain-specific F&B vocabulary)
- Fine-tuned RoBERTa classifies per-sentence sentiment (Yelp-adapted)
- Association: aspects → sentiments in same sentence

**Limitations Addressed**:
- Multi-word aspects (handled via word tokenization)
- Implicit aspects (uses F&B domain-specific keywords)
- Sarcasm (partially mitigated by Yelp fine-tuning on mixed sentiment data)
- Colloquial restaurant language (fine-tuned on Yelp's diverse vocabulary)

### **11.2 Natural Language Inference (NLI)**

**Purpose**: Filter spam/off-topic tweets from Twitter

**Method**: CrossEncoder classification
- Hypothesis: "I am sharing my opinion about the food..."
- Classes: Entailment (review) | Neutral | Contradiction (not review)
- Threshold: 0.55 confidence for valid review acceptance

### **11.3 Sentiment Variance Detection**

**Statistical Approach**:
```python
variance = std(confidence_scores) for each aspect
high_variance = aspect_variance > 0.3
```
**Implication**: High variance = inconsistent customer experience

### **11.4 Cross-Source Consensus Scoring**

**Key Innovation**: Agreement bonus + conflict penalty
- Rewards consistency across sources
- Flags contradictions for manual review
- Weighted by source credibility

### **11.5 Semantic Similarity via Embeddings**

**Technology**: Gemini embeddings (text-embedding-004)
**Use Case**: RAG retrieval for contextual prompt injection

---

## **12. API Endpoints (NLP-focused)**

| Endpoint | Input | NLP Processing | Output |
|----------|-------|-----------------|--------|
| `/analyze/review` | `text` | ABSA pipeline (fine-tuned RoBERTa) | Aspects + sentiments |
| `/analyze/business` | `business_name, location` | Full ABSA + confidence | Aggregated aspects |
| `/insights` | ABSA results | RAG + Gemini LLM | Business recommendations |
| `/frameworks` | Business data | All 8 frameworks | Strategic analysis |
| `/forecast` | `city, category, rating` | XGBoost + RoBERTa sentiment | Rating forecast |
| `/response-template` | `aspect, sentiment` | LLM generation | Owner response |

---

## **13. F&B Domain Specialization**

### **Industry-Specific Features**

1. **Menu Analysis**
   - Item-level sentiment tracking via fine-tuned model
   - BCG Matrix classification (star items vs. dogs)
   - Flavor profile clustering

2. **Service Consistency**
   - Per-aspect variance detection
   - Peak-hours vs. off-hours comparison
   - Staff training effectiveness signals

3. **Pricing Perception**
   - Value-for-money sentiment (fine-tuned model optimized for Yelp price language)
   - Competitor price comparison
   - Margin-impact analysis

4. **Compliance Monitoring**
   - Food safety mentions detection
   - Regulatory keyword flagging
   - Health inspection correlation

---

## **14. Model Performance & Optimization**

### **Efficiency**

- **Batch Inference**: NLI classifier processes all tweets in one call
- **Lazy Loading**: ChromaDB collections created on-demand
- **Token Optimization**: Gemini flash model for cost/speed balance; fine-tuned RoBERTa at 256 tokens max
- **Caching**: Persistent embeddings prevent re-computation
- **Mixed Precision**: Fine-tuned model trained with fp16 for faster inference

### **Scalability**

- **Multi-threading**: Parallel source scraping (Maps, Twitter, News)
- **Async API**: FastAPI async handlers
- **Database**: SQLAlchemy ORM with connection pooling
- **Vector DB**: ChromaDB persistent client for multi-session reuse
- **Fine-tuned Model**: Loaded once at startup, reused for all requests

---

## **15. Quality Assurance**

### **Validation Mechanisms**

1. **ABSA Quality**
   - Keyword coverage for F&B domain
   - Sentiment calibration on Yelp-fine-tuned models
   - Review authenticity via NLI filtering
   - Per-aspect confidence scoring

2. **Confidence Validation**
   - Multi-source agreement bonuses
   - Recency decay for temporal validity
   - Conflict flagging for ambiguous signals

3. **LLM Output**
   - Strict JSON schema validation
   - Expected keys verification per framework
   - Confidence score normalization (0-100)

4. **Fine-tuned Model Validation**
   - Evaluation metrics from training: Macro-averaged F1-score per aspect
   - Per-class precision/recall on Food, Service, Ambiance, Price
   - Baseline comparison: VADER, BERT-base vs. fine-tuned RoBERTa

---

## **16. Key NLP Challenges & Solutions**

| Challenge | Solution |
|-----------|----------|
| Sarcasm detection | Yelp-fine-tuned RoBERTa trained on mixed sentiment data |
| Implicit aspects | Domain-specific F&B keyword lexicon |
| Spam/off-topic reviews | NLI-based filtering with CrossEncoder |
| Cross-lingual reviews | (Future) Add multilingual BERT models |
| Aspect boundaries | Sentence-level aggregation with confidence weighting |
| Outdated reviews | Recency weighting in confidence scoring |
| Source conflicts | Explicit conflict flagging + penalty |
| Restaurant vocabulary | Yelp fine-tuning captures colloquial F&B language |

---

## **17. Fine-Tuning Methodology & Evaluation**

### **17.1 Fine-tuning Process (Research-Grade)**

**Dataset Preparation**:
- Source: Kaggle Yelp Review Full dataset
- Sample sizes: 50K training, 5K validation/test
- Label transformation: 5-star ratings → 3-class sentiment

**Training Pipeline**:
```
1. Load base: cardiffnlp/twitter-roberta-base-sentiment-latest
2. Tokenize with RoBERTa BPE (max 256 tokens)
3. Distributed training on x2 T4 GPUs (fp16 mixed precision)
4. Per-epoch evaluation against test set
5. Save best checkpoint (lowest validation loss)
```

**Expected Performance Gains** (vs. base model):
- Food aspect F1: +8-12% (restaurant-specific vocabulary)
- Service aspect F1: +6-10% (Yelp rich in service language)
- Ambiance aspect F1: +5-8% (decor/setting description style)
- Price aspect F1: +4-7% (value-related discourse)

### **17.2 Evaluation Metrics**

**Per-Aspect Metrics**:
- Precision: True positives / (True positives + False positives)
- Recall: True positives / (True positives + False negatives)
- F1-Score: Harmonic mean of precision and recall
- Accuracy: Overall classification accuracy

**Baseline Comparisons**:
- VADER (lexicon-based): Lower on domain-specific aspects
- BERT-base (zero-shot): Generic sentiment, no F&B adaptation
- Fine-tuned RoBERTa: Expected winner on restaurant reviews

---

## **18. Future NLP Enhancements**

1. **Advanced ABSA**: Aspect-level opinion extraction (no keywords)
2. **Multi-lingual Support**: mBERT or XLM-RoBERTa for global businesses
3. **Aspect-Opinion Pair Extraction**: Joint model for implicit aspects
4. **Zero-shot Classification**: Generalize beyond predefined aspects
5. **Hate Speech Detection**: Safety filtering for moderation
6. **Named Entity Recognition (NER)**: Extract menu items, locations, chef names
7. **Continuous Fine-tuning**: Incorporate user-annotated reviews for model improvement
8. **A/B Testing**: Compare base vs. fine-tuned model on live data


**Project Status**: Production-ready ABSA system with **Yelp-fine-tuned RoBERTa sentiment model**, enterprise-grade confidence scoring, multi-source synthesis, and strategic framework automation.