import google.generativeai as genai
import os
import logging
import json
import chromadb
# embed_content is available via genai.embed_content, so the direct submodule import is not required
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("Gemini API key not found. LLM insights will be disabled.")

# --- NEW: ChromaDB Setup ---
# Initialize Chroma client.
# For production, you might want to use a persistent client:
# chroma_client = chromadb.PersistentClient(path="/path/to/your/db")
# For this example, we'll use an in-memory client.
try:
    chroma_client = chromadb.Client()
    logger.info("ChromaDB in-memory client initialized.")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB client: {e}")
    chroma_client = None

class GeminiEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Custom embedding function for ChromaDB using the Google Gemini API.
    This tells Chroma how to turn your text into vectors.
    """
    def __call__(self, input_texts: chromadb.Documents) -> chromadb.Embeddings:
        if not GEMINI_API_KEY:
            logger.error("Gemini API key not configured for embedding.")
            return [[]] * len(input_texts)
        
        try:
            # Use the recommended embedding model for retrieval
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=input_texts,
                task_type="RETRIEVAL_DOCUMENT" # Specify task type for better embeddings
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error embedding texts with Gemini: {e}")
            return [[]] * len(input_texts)

# --- NEW: Ingestion Function ---
def ingest_reviews_to_chroma(business_name: str, review_texts: List[str]):
    """
    Ingests (embeds and stores) raw review texts into a ChromaDB collection
    for a specific business.
    """
    if not GEMINI_API_KEY or not chroma_client:
        logger.warning("ChromaDB or Gemini API not configured. Skipping ingestion.")
        return

    if not review_texts:
        logger.warning("No review texts provided for ingestion.")
        return

    try:
        # Create a unique collection name for the business
        collection_name = f"reviews_{business_name.replace(' ', '_').lower()}"
        
        # Get or create the collection with our custom embedding function
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=GeminiEmbeddingFunction()
        )
        
        # Create unique IDs for each review
        review_ids = [f"{collection_name}_review_{i}" for i in range(len(review_texts))]
        
        # Use 'upsert' to add new reviews or update existing ones
        # This prevents duplicate work and handles new reviews gracefully
        logger.info(f"Upserting {len(review_texts)} reviews into Chroma collection: {collection_name}")
        collection.upsert(
            documents=review_texts,
            ids=review_ids
        )
        logger.info(f"Ingestion complete for {collection_name}.")

    except Exception as e:
        logger.error(f"Error ingesting reviews into Chroma: {e}")


# --- NEW: RAG Retrieval Function ---
def retrieve_rag_context(business_name: str, absa_results: Dict[str, Any], n_results: int = 3) -> str:
    """
    Retrieves relevant review snippets from ChromaDB based on ABSA results
    to be used as context (the "R" in RAG).
    """
    if not chroma_client:
        logger.warning("Chroma client not available. Skipping RAG retrieval.")
        return "No review context could be retrieved."

    try:
        collection_name = f"reviews_{business_name.replace(' ', '_').lower()}"
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=GeminiEmbeddingFunction() # Must provide the same function
        )
        
        # Generate query texts based on the most important ABSA results
        query_texts = []
        for aspect, data in absa_results.items():
            if isinstance(data, dict):
                sentiment = data.get('overall_sentiment', 'Neutral')
                if sentiment != 'Neutral': # Focus on strong opinions
                    query_texts.append(f"{sentiment} customer feedback about {aspect}")
        
        # Add a general query if no specific aspects were found
        if not query_texts:
            query_texts = [f"Key customer feedback for {business_name}"]

        logger.info(f"Querying Chroma for relevant reviews with: {query_texts}")

        # Query Chroma. It will embed these queries and find the most similar
        # review documents.
        relevant_reviews_data = collection.query(
            query_texts=query_texts,
            n_results=n_results # Get top N results for each query
        )
        
        # Format the retrieved context for the LLM prompt
        retrieved_context = ""
        unique_reviews = set() # Use a set to avoid showing the same review multiple times
        
        if 'documents' in relevant_reviews_data:
            for doc_list in relevant_reviews_data['documents']:
                for doc in doc_list:
                    unique_reviews.add(doc)
        
        if not unique_reviews:
            return "No specific review context found."

        retrieved_context = "--- RELEVANT REVIEW EXAMPLES (retrieved via RAG) ---\n"
        for i, review in enumerate(unique_reviews):
            retrieved_context += f"Context Review {i+1}:\n{review}\n\n"
        
        return retrieved_context

    except Exception as e:
        logger.warning(f"Could not retrieve RAG context from Chroma: {e}")
        return "Error retrieving review context."


# --- MODIFIED: Main Insights Function ---
def generate_business_insights(
    business_name: str,
    business_info: Dict[str, Any],
    absa_results: Dict[str, Any]
    # NOTE: We've removed the 'raw_reviews' argument!
) -> Dict[str, Any]:
    """
    Generate actionable business insights from ABSA results using Gemini LLM,
    augmented with relevant review context retrieved from ChromaDB (RAG).
    
    Args:
        business_name: Name of the business
        business_info: Business information (rating, location, etc.)
        absa_results: ABSA analysis results with aspects and sentiments
        
    Returns:
        Dictionary with strategic recommendations...
    """
    
    if not GEMINI_API_KEY:
        return {
            "error": "Gemini API key not configured",
            "message": "Please set GEMINI_API_KEY in your .env file"
        }
    
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Prepare the analysis summary (your existing function)
        analysis_summary = prepare_analysis_summary(business_name, business_info, absa_results)
        
        # --- RAG Integration ---
        # 1. Retrieve relevant context from ChromaDB based on ABSA results
        logger.info(f"Retrieving RAG context for {business_name}...")
        rag_context = retrieve_rag_context(business_name, absa_results)
        # --- End RAG Integration ---
        
        # 2. Create the modified prompt, injecting the RAG context
        prompt = f"""
You are a business strategy consultant specializing in customer experience and reputation management. 

Analyze the following aspect-based sentiment analysis (ABSA) results and the
RELEVANT REVIEW EXAMPLES provided.

BUSINESS INFORMATION:
- Business Name: {business_name}
- Rating: {business_info.get('rating', 'N/A')}
- Total Ratings: {business_info.get('total_ratings', 'N/A')}
- Location: {business_info.get('address', 'N/A')}

ASPECT-BASED SENTIMENT ANALYSIS RESULTS:
{json.dumps(absa_results, indent=2)}

{rag_context}

Based on the ANALYSIS and the specific REVIEW EXAMPLES, provide strategic recommendations in the following format:

1. **EXECUTIVE SUMMARY**
   - Overall sentiment overview (2-3 sentences)
   - Key strengths to leverage (cite examples from reviews if possible)
   - Critical areas requiring immediate attention (cite examples from reviews if possible)

### 2. STRENGTHS ANALYSIS
- Identify the top-performing aspects (e.g., food, service, ambiance, pricing)
- Explain *why* customers appreciate these aspects, citing examples or keywords from reviews
- Highlight how these strengths differentiate the business from typical competitors

### 3. WEAKNESSES & PAIN POINTS
- List the most frequently criticized aspects and summarize common complaint themes
- Identify potential operational or experiential root causes behind these patterns

### 4. CUSTOMER EXPERIENCE INSIGHTS
- Describe what customers value most in this business (emotionally and practically)
- Note any mismatched expectations between business claims and real experiences

Be specific, data-driven, and practical. Refer to the ABSA data and the
provided review examples to justify your recommendations.

the response should be between 150-175 words only
"""

        # Generate insights using Gemini
        logger.info(f"Generating insights for {business_name} using RAG and Gemini...")
        response = model.generate_content(prompt)
        
        # Parse the response
        insights_text = response.text
        
        # Structure the response
        result = {
            "status": "success",
            "business_name": business_name,
            "analysis_summary": analysis_summary,
            "strategic_insights": insights_text,
            "retrieved_context": rag_context, # Optionally return the context used
            "generated_at": "2025-11-06" # TODO: Use dynamic datetime
        }
        
        logger.info("Insights generated successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate insights using Gemini"
        }

# --- Your other helper functions (unchanged) ---

def prepare_analysis_summary(
    business_name: str,
    business_info: Dict[str, Any],
    absa_results: Dict[str, Any]
) -> Dict[str, Any]:
    # (Your existing code... no changes needed)
    summary = {
        "business_name": business_name,
        "overall_rating": business_info.get('rating', 'N/A'),
        "total_reviews_analyzed": business_info.get('reviews_analyzed', 0),
        "aspects_analyzed": {}
    }
    
    for aspect, data in absa_results.items():
        if isinstance(data, dict) and 'overall_sentiment' in data:
            summary["aspects_analyzed"][aspect] = {
                "overall_sentiment": data.get('overall_sentiment'),
                "total_mentions": data.get('total_mentions', 0),
                "sentiment_breakdown": data.get('sentiment_breakdown', {}),
                "confidence": data.get('average_confidence', 0)
            }
    
    return summary


def generate_quick_summary(absa_results: Dict[str, Any]) -> str:
    # (Your existing code... no changes needed)
    if not absa_results:
        return "No analysis results available."
    
    summary_parts = []
    
    for aspect, data in absa_results.items():
        if isinstance(data, dict) and 'overall_sentiment' in data:
            sentiment = data.get('overall_sentiment')
            mentions = data.get('total_mentions', 0)
            summary_parts.append(f"{aspect}: {sentiment} ({mentions} mentions)")
    
    return " | ".join(summary_parts) if summary_parts else "No aspects found."


def generate_review_response_template(
    aspect: str,
    sentiment: str,
    business_name: str
) -> str:
    # (Your existing code... no changes needed)
    
    if not GEMINI_API_KEY:
        return "Gemini API key not configured"
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
Generate a professional, empathetic review response template for a {sentiment.lower()} review about {aspect.lower()} at {business_name}.

The response should:
- Be 2-3 sentences
- Thank the customer
- Address the specific aspect mentioned
- {f"Acknowledge the issue and show commitment to improvement" if sentiment == "Negative" else "Express appreciation"}
- Include a call-to-action or invitation to return
- Sound genuine and personalized (use [Customer Name] placeholder)

Provide ONLY the response template, no explanations.
"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error generating response template: {e}")
        return f"Error generating template: {str(e)}"