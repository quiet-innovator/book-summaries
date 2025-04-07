from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import openai
import requests
import json
import os
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv  # Added this to load .env file

# Load environment variables from .env
load_dotenv()

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

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# API keys loaded from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Constants
OUTPUT_DIR = "../../public/summaries"  # Path relative to the backend folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
                
                # Skip books without necessary data
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
                # Create cover URL if cover_i exists
                cover_url = ''
                if doc.get('cover_i'):
                    cover_url = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                
                # Extract Work ID if available
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
                    'description': '',  # Open Library search doesn't return descriptions
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
            # Determine if this is a work ID or edition ID
            if is_work:
                url = f"https://openlibrary.org/works/{book_id}.json"
            else:
                url = f"https://openlibrary.org/books/{book_id}.json"
            
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"Open Library API returned {response.status_code} for {url}")
                return None
            
            data = response.json()
            
            # Get cover URL if covers exists
            cover_url = ''
            if data.get('covers', []):
                cover_id = data['covers'][0]
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            
            # Get author information
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
                        # Different structure for edition authors
                        author_key = author_ref['key'].split('/')[-1]
                        try:
                            author_response = requests.get(f"https://openlibrary.org/authors/{author_key}.json")
                            if author_response.status_code == 200:
                                author_data = author_response.json()
                                authors.append(author_data.get('name', 'Unknown'))
                        except:
                            authors.append('Unknown')
            
            # Get description - handle both string and object format
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
            
            # Additional edition-specific fields
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
                
                # Skip items missing essential info
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
                
                # Check if we already have a summary for this book
                book['hasSummary'] = book['id'] in self.processed_books
                
                books.append(book)
        else:
            logger.warning("No 'items' found in the response")
        
        # Determine if there are more books to load
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
    
    # Combine results
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
    
    # Determine if this is a work ID for Open Library
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
        # Try to find the summary file
        filename = f"{OUTPUT_DIR}/{slug}.md"
        if language != "english":
            filename = f"{OUTPUT_DIR}/{slug}-{language}.md"
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse front matter and content
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = parts[1].strip()
                    summary = parts[2].strip()
                    
                    # Parse front matter
                    metadata = {}
                    for line in front_matter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"\'')
                    
                    return jsonify({
                        "title": metadata.get('title', title),
                        "authors": metadata.get('author', authors),
                        "summary": summary,
                        "language": metadata.get('language', language)
                    })
            except Exception as e:
                logger.error(f"Error reading summary file: {e}")
    
    # If we reach here, we need to generate a new summary
    
    # Handle authors as string or list
    if isinstance(authors, str) and ',' in authors:
        authors = [author.strip() for author in authors.split(',')]
    
    # Get book description if available
    description = request.args.get('description', '')
    
    # Generate summary
    try:
        category = request.args.get('category', '')
        
        prompt = f"""
You are a professional book summarizer. Please summarize the book "{title}" by {', '.join(authors) if isinstance(authors, list) else authors}.

Return content in 3 clearly separated sections:
## Short Summary (1–2 sentences)
## Detailed Summary (4–6 paragraphs)
## Key Takeaways (5–10 bullet points)

The summary should be in {language}.
"""
        if description:
            prompt += f"\n\nHere's a description to help you: {description}"
        if category:
            prompt += f"\n\nThis book is categorized as: {category}"
            
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize books clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        
        # Create a new slug if we didn't have one
        if not slug:
            slug = ''.join(c if c.isalnum() or c.isspace() else '-' for c in title.lower())
            slug = '-'.join(slug.split())
            while '--' in slug:
                slug = slug.replace('--', '-')
            if len(slug) > 100:
                slug = slug[:100]
        
        # Add to processed books
        book_id = request.args.get('bookId')
        if book_id:
            book_service.processed_books[book_id] = {
                'title': title,
                'author': authors if isinstance(authors, str) else ', '.join(authors),
                'slug': slug,
                'date_processed': datetime.now().isoformat()
            }
            book_service.save_processed_books()
        
        return jsonify({
            "title": title,
            "authors": authors,
            "summary": summary,
            "language": language
        })
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
    
    # Translate text
    try:
        prompt = f"Translate the following text to {target_language}:\n\n{text}"
        
        response = client.chat.completions.create(
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
                },
                # Add more subcategories as needed
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
                },
                # Add more subcategories as needed
            ]
        }
    ]
    return jsonify(categories)

@app.route('/api/books/category', methods=['GET'])
def get_books_by_category_api():
    """Get books by category from Google Books API"""
    category_code = request.args.get('code')
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 12)), 40)  # Cap at 40 books max
    
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
    
    # Full list of supported languages
    supported_languages = [
        "english", "spanish", "french", "hindi", "german", 
        "italian", "portuguese", "russian", "japanese", 
        "chinese", "korean", "arabic", "dutch", "swedish", 
        "turkish", "polish", "ukrainian", "vietnamese", 
        "thai", "indonesian", "greek", "czech", "romanian", 
        "danish", "finnish", "norwegian", "hebrew", "farsi", 
        "malay", "swahili"
    ]
    
    # Check which language versions exist
    available_languages = []
    book_slug = None
    
    # Find the book's slug by checking processed books
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
    
    # Extract required fields
    title = data.get('title')
    authors = data.get('authors')
    summary = data.get('summary')
    language = data.get('language', 'english')
    book_id = data.get('bookId')
    
    if not title or not authors or not summary or not book_id:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Create book object
        book = {
            'id': book_id,
            'title': title,
            'authors': authors,
            'thumbnailUrl': data.get('thumbnailUrl', ''),
            'publishedDate': data.get('publishedDate', '')
        }
        
        # Create a pending directory for user submissions
        pending_dir = f"{OUTPUT_DIR}/pending"
        os.makedirs(pending_dir, exist_ok=True)
        
        # Create a slug for the filename
        slug = ''.join(c if c.isalnum() or c.isspace() else '-' for c in title.lower())
        slug = '-'.join(slug.split())
        while '--' in slug:
            slug = slug.replace('--', '-')
        if len(slug) > 100:
            slug = slug[:100]
        
        # Add language suffix for non-English summaries
        if language != "english":
            filename = f"{pending_dir}/{slug}-{language}.md"
        else:
            filename = f"{pending_dir}/{slug}.md"
        
        # Format authors
        if isinstance(authors, list):
            author_text = ', '.join(authors)
        else:
            author_text = str(authors)
        
        # Generate metadata
        pub_date = datetime.today().strftime('%Y-%m-%d')
        description = f"Summary of the book '{title}' by {author_text}."
        
        # Generate tags (simplified)
        tags = ["user-submitted", "pending-review"]
        tags_json = json.dumps(tags)
        
        # Compile front matter
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
        
        # Add optional fields if available
        if data.get('thumbnailUrl'):
            md_content += f'thumbnailUrl: "{data.get("thumbnailUrl")}"\n'
        if data.get('publishedDate'):
            md_content += f'publishedDate: "{data.get("publishedDate")}"\n'
        
        # Close front matter and add summary
        md_content += f"---\n\n{summary}\n"
        
        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        # Return success response
        return jsonify({
            "success": True,
            "message": "Summary submitted successfully. It will be reviewed before being published."
        })
    except Exception as e:
        logger.error(f"Error submitting summary: {e}")
        return jsonify({"error": f"Error submitting summary: {str(e)}"}), 500

# Main function to run the app
# Add this right after the other @app.route() definitions, 
# before the if __name__ == '__main__':' block at the end of the file

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

# Then keep the existing if __name__ == '__main__': block as it was
if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create pending directory for user submissions
    os.makedirs(f"{OUTPUT_DIR}/pending", exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=True)