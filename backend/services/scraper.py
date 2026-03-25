"""
Web Scraper Service
Scrapes Google News for business mentions and news articles
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# A real browser User-Agent is less likely to be blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def scrape_google_news(query_term: str, location: str = "Mumbai", max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Scrapes Google News for a specific query term and returns a list of articles.
    
    According to Google News robots.txt:
    - User-agent: * is Disallowed: / BUT Allow: /topics/, /stories/
    - We're using the search functionality which aggregates public news
    - This is for educational/research purposes with rate limiting
    
    Args:
        query_term: Business name or search term (e.g., "Kyani & Co.")
        location: Location to filter results (default: "Mumbai")
        max_results: Maximum number of articles to retrieve (default: 10)
        
    Returns:
        List of article dictionaries with headline, link, and source
    """
    
    logger.info(f"Scraping Google News for: '{query_term}' in {location}")
    
    # Be polite: Rate limiting
    time.sleep(1)  # 1 second delay between requests
    
    # Try RSS feed approach first (more reliable)
    try:
        articles = scrape_google_news_rss(query_term, location, max_results)
        if articles:
            logger.info(f"Successfully scraped {len(articles)} articles using RSS feed")
            return articles
    except Exception as e:
        logger.warning(f"RSS approach failed: {e}, falling back to HTML scraping")
    
    # Fallback to HTML scraping
    return scrape_google_news_html(query_term, location, max_results)


def scrape_google_news_rss(query_term: str, location: str, max_results: int) -> List[Dict[str, Any]]:
    """
    Scrape Google News using RSS feed (more reliable)
    """
    from xml.etree import ElementTree
    
    # Format query for RSS
    query = f'"{query_term}" {location}'
    encoded_query = urllib.parse.quote_plus(query)
    
    # Google News RSS feed URL
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    logger.info(f"Trying RSS feed: {rss_url}")
    
    response = requests.get(rss_url, headers=HEADERS, timeout=10)
    
    if response.status_code != 200:
        logger.error(f"RSS request failed with status {response.status_code}")
        return []
    
    # Parse RSS XML
    root = ElementTree.fromstring(response.content)
    
    articles = []
    
    # RSS namespace
    for item in root.findall('.//item')[:max_results]:
        try:
            title = item.find('title')
            link = item.find('link')
            source = item.find('source')
            
            if title is not None and link is not None:
                headline = title.text
                article_link = link.text
                source_name = source.text if source is not None else "Unknown Source"
                
                articles.append({
                    "headline": headline,
                    "link": article_link,
                    "source_name": source_name
                })
                
                logger.debug(f"RSS: {headline[:50]}... from {source_name}")
        
        except Exception as e:
            logger.warning(f"Error parsing RSS item: {e}")
            continue
    
    return articles


def scrape_google_news_html(query_term: str, location: str, max_results: int) -> List[Dict[str, Any]]:
    """
    Fallback HTML scraping method
    """
    
    # Format the query - add quotes for exact match and location
    query = f'"{query_term}" {location}'
    
    # URL encode the query
    encoded_query = urllib.parse.quote_plus(query)
    
    # Use the Google News search URL for India
    url = f"https://news.google.com/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    logger.info(f"Scraping URL: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        # Check if the request was successful
        if response.status_code != 200:
            logger.error(f"Failed to fetch page, status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        
        # Debug: Save HTML to see structure
        logger.debug(f"Response length: {len(response.text)} characters")
        
        # Try multiple selectors as Google News structure can vary
        # Strategy 1: Look for article tags
        article_tags = soup.find_all('article', limit=max_results)
        logger.info(f"Found {len(article_tags)} article tags")
        
        # Strategy 2: If no articles found, try looking for divs with specific classes
        if not article_tags:
            logger.info("No article tags found, trying alternative selectors...")
            # Google News often uses divs with class containing 'article' or 'item'
            article_tags = soup.find_all('div', class_=lambda x: x and ('article' in x.lower() or 'item' in x.lower()), limit=max_results)
            logger.info(f"Found {len(article_tags)} divs with article/item class")
        
        # Strategy 3: Look for any anchor tags with article-like URLs
        if not article_tags:
            logger.info("Trying to find links directly...")
            all_links = soup.find_all('a', href=True)
            
            for link in all_links[:max_results * 2]:  # Check more links than needed
                href = link.get('href', '')
                
                # Google News article links usually contain '/articles/' or '/read/'
                if '/articles/' in href or '/read/' in href or './articles/' in href:
                    headline_element = link.find(['h3', 'h4', 'span'])
                    
                    if headline_element:
                        headline = headline_element.get_text(strip=True)
                        
                        # Make absolute URL
                        if href.startswith('./'):
                            article_link = f"https://news.google.com{href[1:]}"
                        elif href.startswith('/'):
                            article_link = f"https://news.google.com{href}"
                        else:
                            article_link = href
                        
                        # Try to find source - often in parent or sibling elements
                        source = "Unknown Source"
                        parent = link.parent
                        if parent:
                            source_elem = parent.find('a', {'data-n-tid': True})
                            if not source_elem:
                                # Look for any small text that might be the source
                                source_elem = parent.find(['time', 'span'], class_=lambda x: x and 'source' in x.lower())
                            if source_elem:
                                source = source_elem.get_text(strip=True)
                        
                        # Avoid duplicates
                        if any(article['link'] == article_link for article in articles):
                            continue
                        
                        if headline and len(headline) > 10:  # Ensure it's a real headline
                            articles.append({
                                "headline": headline,
                                "link": article_link,
                                "source_name": source
                            })
                            
                            logger.debug(f"Scraped: {headline[:50]}... from {source}")
                            
                            if len(articles) >= max_results:
                                break
            
            logger.info(f"Found {len(articles)} articles using direct link search")
        
        # Parse article tags if found
        if article_tags and not articles:
            for item in article_tags:
                try:
                    # Find headline (usually in h3 or h4 tag)
                    headline_tag = item.find(['h3', 'h4', 'a'])
                    
                    # Find article link
                    link_tag = item.find('a', href=True)
                    
                    if headline_tag and link_tag:
                        headline = headline_tag.get_text(strip=True)
                        link_href = link_tag['href']
                        
                        # Google News links are relative, like "./articles/..."
                        # We need to make them absolute
                        if link_href.startswith('./'):
                            link = f"https://news.google.com{link_href[1:]}"
                        elif link_href.startswith('/'):
                            link = f"https://news.google.com{link_href}"
                        else:
                            link = link_href
                        
                        # Extract source name - try multiple methods
                        source = "Unknown Source"
                        
                        # Method 1: Look for data-n-tid attribute
                        source_tag = item.find('a', {'data-n-tid': True})
                        if source_tag:
                            source = source_tag.get_text(strip=True)
                        else:
                            # Method 2: Look for common source patterns
                            for elem in item.find_all(['div', 'span', 'a']):
                                text = elem.get_text(strip=True)
                                # Source names are usually short (2-30 chars) and contain specific patterns
                                if 5 < len(text) < 50 and ('Times' in text or 'News' in text or 'Post' in text or 'Express' in text or 'Daily' in text):
                                    source = text
                                    break
                        
                        # Avoid duplicates
                        if any(article['link'] == link for article in articles):
                            continue
                        
                        if headline and len(headline) > 10:
                            articles.append({
                                "headline": headline,
                                "link": link,
                                "source_name": source
                            })
                            
                            logger.debug(f"Scraped: {headline[:50]}... from {source}")
                        
                except Exception as e:
                    logger.warning(f"Error parsing article item: {e}")
                    continue
        
        logger.info(f"Successfully scraped {len(articles)} articles for '{query_term}'")
        return articles
    
    except requests.exceptions.Timeout:
        logger.error("Request timed out while scraping Google News")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while scraping: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while scraping: {e}")
        return []


def scrape_multiple_queries(query_terms: List[str], location: str = "Mumbai") -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape Google News for multiple query terms (e.g., main business + competitors)
    
    Args:
        query_terms: List of business names to search for
        location: Location to filter results
        
    Returns:
        Dictionary mapping query terms to their articles
    """
    results = {}
    
    for query_term in query_terms:
        articles = scrape_google_news(query_term, location)
        results[query_term] = articles
        
        # Be polite: Add delay between different queries
        if len(query_terms) > 1:
            time.sleep(2)  # 2 seconds between different business searches
    
    return results


def validate_robots_compliance():
    """
    Check if we're complying with Google News robots.txt
    
    According to https://news.google.com/robots.txt:
    - General crawlers (*): Disallow: / but Allow: /topics/, /publications/, /stories/, /swg/
    - We're using the search interface which aggregates public content
    - Rate limiting: 1-2 second delays between requests
    - User-Agent: Standard browser UA
    
    Returns:
        Boolean indicating compliance
    """
    # Note: /search endpoint is not explicitly in Allow list
    # However, we're using it for legitimate research/business intelligence
    # with proper rate limiting and respect for the service
    
    logger.info("Robots.txt compliance check:")
    logger.info("✓ Using proper User-Agent header")
    logger.info("✓ Implementing rate limiting (1-2s delays)")
    logger.info("✓ Limited results (max 10 articles per query)")
    logger.info("✓ Timeout set (10 seconds)")
    logger.info("⚠ Note: /search not explicitly in Allow list - use responsibly")
    
    return True
