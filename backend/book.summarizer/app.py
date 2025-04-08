import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from pathlib import Path
from dotenv import load_dotenv

# Build the path to the .env file: go up three levels from the current file's directory
env_path = Path(__file__).parent.parent.parent / ".env"
print("Loading .env from:", env_path.resolve())
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("book_api_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API keys loaded from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("Loaded OPENAI_API_KEY:", repr(OPENAI_API_KEY))

# Initialize OpenAI client using the standard method
import openai
openai.api_key = OPENAI_API_KEY

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Constants
# Updated OUTPUT_DIR to point to your website's content folder for book summaries.
OUTPUT_DIR = "C:/Users/alime/book-summaries/src/content/books"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_amazon_link(title, authors):
    """Generate Amazon affiliate link"""
    base_url = "https://www.amazon.com/s"
    query = f"{title} {' '.join(authors)}".replace(' ', '+')
    return f"{base_url}?k={query}&tag=gmh07-20" 

def suggest_related_books(title, category=None):
    """Suggest related books based on title or category"""
    related_books = [
        "The 7 Habits of Highly Effective People by Stephen Covey",
        "Atomic Habits by James Clear",
        "Deep Work by Cal Newport"
    ]
    return related_books

def extract_quotes(summary):
    """Extract or generate meaningful quotes from the summary"""
    quotes = [
        "A powerful quote capturing the book's essence",
        "An insightful line that resonates with the book's theme",
        "A thought-provoking statement from the text"
    ]
    return quotes

def format_summary(title, authors, description, gpt_summary, language='english'):
    """Format the summary in the desired Markdown structure"""
    # Ensure authors is a string
    if isinstance(authors, list):
        authors = ', '.join(authors)
    
    # Generate links and suggestions
    amazon_link = generate_amazon_link(title, [authors])
    related_books = suggest_related_books(title)
    quotes = extract_quotes(gpt_summary)
    
    # Parse the GPT-generated summary
    sections = gpt_summary.split('## ')
    
    # Extract sections, with fallback values
    short_summary = sections[1].split('\n')[0].strip() if len(sections) > 1 else "A brief overview of the book."
    detailed_summary = sections[2] if len(sections) > 2 else "Detailed exploration of the book's content."
    key_takeaways = sections[3].split('\n') if len(sections) > 3 else ["Key insight 1", "Key insight 2"]
    
    # Clean up key takeaways
    key_takeaways = [takeaway.strip().replace('- ', '') for takeaway in key_takeaways if takeaway.strip()]
    
    summary_content = f"""---
title: "{title}"
author: "{authors}"
pubDate: "{datetime.now().strftime('%Y-%m-%d')}"
description: "{description or 'A comprehensive book summary'}"
language: "{language}"
amazonLink: "{amazon_link}"
---

## Intro Sentence
{short_summary}

## The Big Idea
A concise statement of the book's central thesis or most important concept.

## Core Summary
{detailed_summary.strip()}

## Key Takeaways
{''.join([f"🔑 {takeaway}\n" for takeaway in key_takeaways])}

## Apply This Now
1. 🎯 First actionable step derived from the book
2. 🛠 Second practical application
3. 🌱 Third implementable strategy

## Quotes to Remember
1. "{quotes[0]}"
2. "{quotes[1]}"
3. "{quotes[2]}"

## Get this Book Now
[Buy on Amazon]({amazon_link})

## Pair With
1. {related_books[0]}
2. {related_books[1]}
3. {related_books[2]}

## About the Author
{authors} is a notable author known for their significant contributions to literature and writing. Their other works include [List other books by the author if available].
"""
    return summary_content

# Book Service class
class BookService:
    """Service to handle book data and API interactions"""
    
    def __init__(self):
        self.processed_books = self._load_processed_books()
    
    def _load_processed_books(self):
        """Load previously processed books"""
        processed_books_file = os.path.join(OUTPUT_DIR, "processed_books.json")
        if os.path.exists(processed_books_file):
            try:
                with open(processed_books_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading processed books: {e}")
        return {}
    
    def save_processed_books(self):
        """Save processed books to file"""
        processed_books_file = os.path.join(OUTPUT_DIR, "processed_books.json")
        try:
            with open(processed_books_file, 'w') as f:
                json.dump(self.processed_books, f)
            logger.info(f"Saved {len(self.processed_books)} processed books")
        except Exception as e:
            logger.error(f"Error saving processed books: {e}")
    
    def search_google_books(self, query, max_results=10):
        """Search for books using Google Books API"""
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&key={GOOGLE_BOOKS_API_KEY}"
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"Google Books API returned {response.status_code}")
                return []
            
            data = response.json()
            if 'items' not in data:
                return []
                
            books = []
            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                if not volume_info.get('title'):
                    continue
                book = {
                    'source': 'Google Books',
                    'id': item.get('id'),
                    'title': volume_info.get('title', 'Unknown'),
                    'authors': volume_info.get('authors', ['Unknown']),
                    'publishedDate': volume_info.get('publishedDate', ''),
                    'description': volume_info.get('description', ''),
                    'pageCount': volume_info.get('pageCount'),
                    'categories': volume_info.get('categories', []),
                    'averageRating': volume_info.get('averageRating'),
                    'ratingsCount': volume_info.get('ratingsCount', 0),
                    'language': volume_info.get('language', 'en'),
                    'thumbnailUrl': volume_info.get('imageLinks', {}).get('thumbnail', '')
                }
                books.append(book)
            return books
        except Exception as e:
            logger.error(f"Error searching Google Books: {e}")
            return []
    
    def search_open_library(self, query, max_results=10):
        """Search for books using Open Library Search API"""
        try:
            url = f"https://openlibrary.org/search.json?q={query}&limit={max_results}"
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"Open Library API returned {response.status_code}")
                return []
            
            data = response.json()
            if 'docs' not in data:
                return []
                
            books = []
            for doc in data['docs']:
                cover_url = ''
                if doc.get('cover_i'):
                    cover_url = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                work_id = None
                if doc.get('key'):
                    if doc.get('key').startswith('/works/'):
                        work_id = doc.get('key').split('/')[-1]
                book = {
                    'source': 'Open Library',
                    'id': doc.get('key', '').split('/')[-1] if doc.get('key') else '',
                    'work_id': work_id,
                    'title': doc.get('title', 'Unknown'),
                    'authors': doc.get('author_name', ['Unknown']),
                    'publishedDate': str(doc.get('first_publish_year', '')),
                    'description': '',
                    'pageCount': doc.get('number_of_pages_median'),
                    'categories': doc.get('subject', []),
                    'thumbnailUrl': cover_url
                }
                books.append(book)
            return books
        except Exception as e:
            logger.error(f"Error searching Open Library: {e}")
            return []
    
    def get_book_details_open_library(self, book_id, is_work=True):
        """Get detailed book information from Open Library"""
        try:
            if is_work:
                url = f"https://openlibrary.org/works/{book_id}.json"
            else:
                url = f"https://openlibrary.org/books/{book_id}.json"
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"Open Library API returned {response.status_code} for {url}")
                return None
            data = response.json()
            cover_url = ''
            if data.get('covers', []):
                cover_id = data['covers'][0]
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            authors = []
            if 'authors' in data:
                for author_ref in data['authors']:
                    if isinstance(author_ref, dict) and 'author' in author_ref:
                        author_key = author_ref['author']['key'].split('/')[-1]
                        try:
                            author_response = requests.get(f"https://openlibrary.org/authors/{author_key}.json")
                            if author_response.status_code == 200:
                                author_data = author_response.json()
                                authors.append(author_data.get('name', 'Unknown'))
                        except:
                            authors.append('Unknown')
                    elif isinstance(author_ref, dict) and 'key' in author_ref:
                        author_key = author_ref['key'].split('/')[-1]
                        try:
                            author_response = requests.get(f"https://openlibrary.org/authors/{author_key}.json")
                            if author_response.status_code == 200:
                                author_data = author_response.json()
                                authors.append(author_data.get('name', 'Unknown'))
                        except:
                            authors.append('Unknown')
            description = ""
            if 'description' in data:
                if isinstance(data['description'], str):
                    description = data['description']
                elif isinstance(data['description'], dict) and 'value' in data['description']:
                    description = data['description']['value']
            book_details = {
                'source': 'Open Library',
                'id': book_id,
                'title': data.get('title', 'Unknown'),
                'subtitle': data.get('subtitle', ''),
                'authors': authors,
                'description': description,
                'subjects': data.get('subjects', []),
                'thumbnailUrl': cover_url
            }
            if not is_work:
                book_details.update({
                    'isbn_10': data.get('isbn_10', []),
                    'isbn_13': data.get('isbn_13', []),
                    'publish_date': data.get('publish_date', ''),
                    'publishers': data.get('publishers', []),
                    'number_of_pages': data.get('number_of_pages'),
                    'physical_format': data.get('physical_format', '')
                })
            return book_details
        except Exception as e:
            logger.error(f"Error getting Open Library details for {book_id}: {e}")
            return None
    
    def get_book_details_google(self, book_id):
        """Get detailed book information from Google Books"""
        try:
            url = f"https://www.googleapis.com/books/v1/volumes/{book_id}?key={GOOGLE_BOOKS_API_KEY}"
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"Google Books API returned {response.status_code} for {url}")
                return None
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            book_details = {
                'source': 'Google Books',
                'id': book_id,
                'title': volume_info.get('title', 'Unknown'),
                'subtitle': volume_info.get('subtitle', ''),
                'authors': volume_info.get('authors', ['Unknown']),
                'publishedDate': volume_info.get('publishedDate', 'Unknown'),
                'description': volume_info.get('description', ''),
                'pageCount': volume_info.get('pageCount'),
                'categories': volume_info.get('categories', []),
                'averageRating': volume_info.get('averageRating'),
                'ratingsCount': volume_info.get('ratingsCount', 0),
                'language': volume_info.get('language', ''),
                'thumbnailUrl': volume_info.get('imageLinks', {}).get('thumbnail', '')
            }
            return book_details
        except Exception as e:
            logger.error(f"Error getting Google Books details for {book_id}: {e}")
            return None
    
    def get_book_details(self, source, book_id, is_work=True):
        """Get detailed book information from appropriate source"""
        if source == 'Google Books':
            return self.get_book_details_google(book_id)
        elif source == 'Open Library':
            return self.get_book_details_open_library(book_id, is_work)
        else:
            logger.warning(f"Unknown source: {source}")
            return None

def get_books_by_category(self, category_code, page=1, limit=12):
    """Get books by category from Google Books API"""
    try:
        offset = (page - 1) * limit
        query = f"subject:{category_code}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={limit}&startIndex={offset}&orderBy=relevance&key={GOOGLE_BOOKS_API_KEY}"
        logger.info(f"Attempting to fetch books with URL: {url}")
        response = requests.get(url)
        logger.info(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Google Books API returned {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return {"results": [], "hasMore": False, "totalCount": 0, "page": page}
        data = response.json()
        logger.info(f"Total items found: {data.get('totalItems', 0)}")
        total_items = data.get('totalItems', 0)
        books = []
        if 'items' in data:
            logger.info(f"Number of items in response: {len(data['items'])}")
            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                if not volume_info.get('title'):
                    continue
                book = {
                    'id': item.get('id'),
                    'title': volume_info.get('title', 'Unknown'),
                    'authors': volume_info.get('authors', ['Unknown']),
                    'publishedDate': volume_info.get('publishedDate', ''),
                    'description': volume_info.get('description', ''),
                    'pageCount': volume_info.get('pageCount'),
                    'categories': volume_info.get('categories', []),
                    'rating': volume_info.get('averageRating'),
                    'ratingsCount': volume_info.get('ratingsCount', 0),
                    'thumbnailUrl': volume_info.get('imageLinks', {}).get('thumbnail', '')
                }
                book['hasSummary'] = book['id'] in self.processed_books
                books.append(book)
        else:
            logger.warning("No 'items' found in the response")
        has_more = (offset + limit) < total_items
        logger.info(f"Returning {len(books)} books, hasMore: {has_more}")
        return {
            "results": books,
            "hasMore": has_more,
            "totalCount": total_items,
            "page": page
        }
    except Exception as e:
        logger.error(f"Error fetching books by category: {e}")
        return {"results": [], "hasMore": False, "totalCount": 0, "page": page}

# Initialize the book service
book_service = BookService()

# API Endpoints

@app.route('/api/book/search', methods=['GET'])
def search_books_api():
    """Search for books using both Google Books and Open Library APIs"""
    query = request.args.get('query', '')
    max_results = int(request.args.get('limit', 10))
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    google_books = book_service.search_google_books(query, max_results // 2)
    open_library_books = book_service.search_open_library(query, max_results // 2)
    results = google_books + open_library_books
    return jsonify({
        "query": query,
        "results": results
    })

@app.route('/api/book/details', methods=['GET'])
def get_book_details_api():
    """Get detailed information about a specific book"""
    book_id = request.args.get('id')
    source = request.args.get('source')
    if not book_id or not source:
        return jsonify({"error": "Book ID and source are required"}), 400
    is_work = request.args.get('is_work', 'true').lower() == 'true'
    book_details = book_service.get_book_details(source, book_id, is_work)
    if book_details is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book_details)

@app.route('/api/book/summary', methods=['GET'])
def get_book_summary_api():
    """Generate a summary for a book using GPT-3.5"""
    title = request.args.get('title')
    authors = request.args.get('authors', 'Unknown')
    language = request.args.get('language', 'english')
    slug = request.args.get('slug')
    if not title and not slug:
        return jsonify({"error": "Book title or slug is required"}), 400
    if slug:
        try:
            filename = f"{OUTPUT_DIR}/{slug}.md"
            if language != "english":
                filename = f"{OUTPUT_DIR}/{slug}-{language}.md"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading existing summary: {e}")
    if isinstance(authors, str) and ',' in authors:
        authors = [author.strip() for author in authors.split(',')]
    description = request.args.get('description', '')
    try:
        prompt = f"""
You are a professional book summarizer. Create a comprehensive summary of "{title}" by {', '.join(authors) if isinstance(authors, list) else authors}.

Generate the summary in these clear sections:
## Short Summary (1–2 sentences introducing the book)
## Detailed Summary (4–6 paragraphs exploring the book's content)
## Key Takeaways (5–10 bullet points of core insights)

The summary should be in {language}, focusing on the book's core message, key themes, and most important insights.
"""
        if description:
            prompt += f"\n\nBook Description: {description}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert book summarizer who creates engaging, insightful summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        gpt_summary = response.choices[0].message.content
        if not slug:
            slug = ''.join(c if c.isalnum() or c.isspace() else '-' for c in title.lower())
            slug = '-'.join(slug.split())
            while '--' in slug:
                slug = slug.replace('--', '-')
            if len(slug) > 100:
                slug = slug[:100]
        formatted_summary = format_summary(title, authors, description, gpt_summary, language)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = f"{OUTPUT_DIR}/{slug}.md"
        if language != "english":
            filename = f"{OUTPUT_DIR}/{slug}-{language}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_summary)
        book_id = request.args.get('bookId')
        if book_id:
            book_service.processed_books[book_id] = {
                'title': title,
                'author': authors if isinstance(authors, str) else ', '.join(authors),
                'slug': slug,
                'date_processed': datetime.now().isoformat()
            }
            book_service.save_processed_books()
        return formatted_summary
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return jsonify({"error": f"Failed to generate summary: {str(e)}"}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text_api():
    """Translate text using GPT-3.5"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    text = data.get('text')
    target_language = data.get('language', 'spanish')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        prompt = f"Translate the following text to {target_language}:\n\n{text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        translated_text = response.choices[0].message.content
        return jsonify({
            "original": text,
            "translated": translated_text,
            "language": target_language
        })
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages_api():
    """Get available languages"""
    return jsonify({
        "languages": [
            {"code": "english", "name": "English"},
            {"code": "spanish", "name": "Spanish"},
            {"code": "french", "name": "French"},
            {"code": "hindi", "name": "Hindi"},
            {"code": "german", "name": "German"},
            {"code": "italian", "name": "Italian"},
            {"code": "portuguese", "name": "Portuguese"},
            {"code": "russian", "name": "Russian"},
            {"code": "japanese", "name": "Japanese"},
            {"code": "chinese", "name": "Chinese"},
            {"code": "korean", "name": "Korean"},
            {"code": "arabic", "name": "Arabic"},
            {"code": "dutch", "name": "Dutch"},
            {"code": "swedish", "name": "Swedish"},
            {"code": "turkish", "name": "Turkish"},
            {"code": "polish", "name": "Polish"},
            {"code": "ukrainian", "name": "Ukrainian"},
            {"code": "vietnamese", "name": "Vietnamese"},
            {"code": "thai", "name": "Thai"},
            {"code": "indonesian", "name": "Indonesian"},
            {"code": "greek", "name": "Greek"},
            {"code": "czech", "name": "Czech"},
            {"code": "romanian", "name": "Romanian"},
            {"code": "danish", "name": "Danish"},
            {"code": "finnish", "name": "Finnish"},
            {"code": "norwegian", "name": "Norwegian"},
            {"code": "hebrew", "name": "Hebrew"},
            {"code": "farsi", "name": "Farsi"},
            {"code": "malay", "name": "Malay"},
            {"code": "swahili", "name": "Swahili"}
        ]
    })

@app.route('/api/categories', methods=['GET'])
def get_categories_api():
    """Get categorized book structure for UI"""
    categories = [
        {
            "name": "Fiction",
            "code": "fiction",
            "subcategories": [
                {
                    "name": "Literature",
                    "code": "literary+fiction",
                    "subcategories": [
                        {"name": "Literary Fiction", "code": "literary+fiction"},
                        {"name": "Classics", "code": "classic+literature"},
                        {"name": "Historical Fiction", "code": "historical+fiction"},
                        {"name": "Short Stories", "code": "short+stories"},
                        {"name": "Women's Fiction", "code": "womens+fiction"},
                        {"name": "Men's Fiction", "code": "mens+fiction"}
                    ]
                }
            ]
        },
        {
            "name": "Non-Fiction",
            "code": "nonfiction",
            "subcategories": [
                {
                    "name": "Self-Help",
                    "code": "self-help",
                    "subcategories": [
                        {"name": "Personal Development", "code": "personal+development"},
                        {"name": "Motivation", "code": "motivation+self-help"},
                        {"name": "Mindfulness and Meditation", "code": "mindfulness+meditation"}
                    ]
                }
            ]
        }
    ]
    return jsonify(categories)

@app.route('/api/books/category', methods=['GET'])
def get_books_by_category_api():
    """Get books by category from Google Books API"""
    category_code = request.args.get('code')
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 12)), 40)
    if not category_code:
        return jsonify({"error": "Category code is required"}), 400
    result = book_service.get_books_by_category(category_code, page, limit)
    return jsonify(result)

@app.route('/api/book/available-languages', methods=['GET'])
def get_available_languages_for_book():
    """Get available languages for a specific book summary"""
    book_id = request.args.get('id')
    if not book_id:
        return jsonify({"error": "Book ID is required"}), 400
    supported_languages = [
        "english", "spanish", "french", "hindi", "german", 
        "italian", "portuguese", "russian", "japanese", 
        "chinese", "korean", "arabic", "dutch", "swedish", 
        "turkish", "polish", "ukrainian", "vietnamese", 
        "thai", "indonesian", "greek", "czech", "romanian", 
        "danish", "finnish", "norwegian", "hebrew", "farsi", 
        "malay", "swahili"
    ]
    available_languages = []
    book_slug = None
    for id, book_data in book_service.processed_books.items():
        if id == book_id:
            title = book_data.get('title', '')
            book_slug = ''.join(c if c.isalnum() or c.isspace() else '-' for c in title.lower())
            book_slug = '-'.join(book_slug.split())
            while '--' in book_slug:
                book_slug = book_slug.replace('--', '-')
            if len(book_slug) > 100:
                book_slug = book_slug[:100]
            break
    if book_slug:
        for language in supported_languages:
            filename = f"{OUTPUT_DIR}/{book_slug}.md"
            if language != "english":
                filename = f"{OUTPUT_DIR}/{book_slug}-{language}.md"
            if os.path.exists(filename):
                available_languages.append(language)
    return jsonify({"bookId": book_id, "languages": available_languages})

@app.route('/api/book/submit-summary', methods=['POST'])
def submit_book_summary():
    """Submit a user-generated book summary"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    title = data.get('title')
    authors = data.get('authors')
    summary = data.get('summary')
    language = data.get('language', 'english')
    book_id = data.get('bookId')
    if not title or not authors or not summary or not book_id:
        return jsonify({"error": "Missing required fields"}), 400
    try:
        book = {
            'id': book_id,
            'title': title,
            'authors': authors,
            'thumbnailUrl': data.get('thumbnailUrl', ''),
            'publishedDate': data.get('publishedDate', '')
        }
        pending_dir = f"{OUTPUT_DIR}/pending"
        os.makedirs(pending_dir, exist_ok=True)
        slug = ''.join(c if c.isalnum() or c.isspace() else '-' for c in title.lower())
        slug = '-'.join(slug.split())
        while '--' in slug:
            slug = slug.replace('--', '-')
        if len(slug) > 100:
            slug = slug[:100]
        if language != "english":
            filename = f"{pending_dir}/{slug}-{language}.md"
        else:
            filename = f"{pending_dir}/{slug}.md"
        if isinstance(authors, list):
            author_text = ', '.join(authors)
        else:
            author_text = str(authors)
        pub_date = datetime.today().strftime('%Y-%m-%d')
        description = f"Summary of the book '{title}' by {author_text}."
        tags = ["user-submitted", "pending-review"]
        tags_json = json.dumps(tags)
        md_content = (
            f"---\n"
            f'title: "{title}"\n'
            f'pubDate: "{pub_date}"\n'
            f'description: "{description}"\n'
            f'author: "{author_text}"\n'
            f'language: "{language}"\n'
            f'tags: {tags_json}\n'
            f'bookId: "{book_id}"\n'
            f'status: "pending"\n'
        )
        if data.get('thumbnailUrl'):
            md_content += f'thumbnailUrl: "{data.get("thumbnailUrl")}"\n'
        if data.get('publishedDate'):
            md_content += f'publishedDate: "{data.get("publishedDate")}"\n'
        md_content += f"---\n\n{summary}\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)
        return jsonify({
            "success": True,
            "message": "Summary submitted successfully. It will be reviewed before being published."
        })
    except Exception as e:
        logger.error(f"Error submitting summary: {e}")
        return jsonify({"error": f"Error submitting summary: {str(e)}"}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "API running",
        "endpoints": [
            "/api/book/search",
            "/api/book/details",
            "/api/book/summary",
            "/api/translate",
            "/api/languages",
            "/api/categories",
            "/api/books/category",
            "/api/book/available-languages",
            "/api/book/submit-summary"
        ]
    })

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/pending", exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=True)
