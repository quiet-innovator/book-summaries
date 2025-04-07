// src/components/AddBookForm.jsx
import { useState } from 'react';

export default function AddBookForm({ lang }) {
  const [step, setStep] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [summary, setSummary] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
  
  // Search for a book
  const searchBook = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      setError('Please enter a book title or author');
      return;
    }
    
    setIsSearching(true);
    setError('');
    setSearchResults([]);
    
    try {
      const response = await fetch(`${API_URL}/api/book/search?query=${encodeURIComponent(searchQuery)}`);
      
      if (!response.ok) {
        throw new Error('Failed to search for books');
      }
      
      const data = await response.json();
      setSearchResults(data.results);
      
      if (data.results.length === 0) {
        setError('No books found. Try a different search term.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSearching(false);
    }
  };
  
  // Select a book from search results
  const selectBook = (book) => {
    setSelectedBook(book);
    setStep(2);
  };
  
  // Submit the book summary
  const submitSummary = async (e) => {
    e.preventDefault();
    
    if (!summary.trim()) {
      setError('Please enter a summary');
      return;
    }
    
    if (!selectedBook) {
      setError('Please select a book first');
      setStep(1);
      return;
    }
    
    setIsSubmitting(true);
    setError('');
    
    try {
      const response = await fetch(`${API_URL}/api/book/submit-summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: selectedBook.title,
          authors: selectedBook.authors,
          bookId: selectedBook.id,
          summary,
          language: lang === 'en' ? 'english' : lang === 'es' ? 'spanish' : lang === 'fr' ? 'french' : 'hindi',
          thumbnailUrl: selectedBook.thumbnailUrl,
          publishedDate: selectedBook.publishedDate,
          source: selectedBook.source
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to submit summary');
      }
      
      setSuccess('Summary submitted successfully! It will be reviewed before being published.');
      
      // Reset form
      setTimeout(() => {
        setStep(1);
        setSearchQuery('');
        setSearchResults([]);
        setSelectedBook(null);
        setSummary('');
        setSuccess('');
      }, 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Go back to search
  const goBackToSearch = () => {
    setStep(1);
    setSelectedBook(null);
  };

  return (
    <div className="add-book-form">
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      {step === 1 ? (
        <>
          <h2>Step 1: Find a Book</h2>
          <form onSubmit={searchBook} className="search-form">
            <div className="search-container">
              <input 
                type="text" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter book title or author"
                className="search-input"
              />
              <button 
                type="submit" 
                disabled={isSearching} 
                className="search-button"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
          
          {searchResults.length > 0 && (
            <div className="search-results">
              <h3>Select a Book</h3>
              <div className="results-grid">
                {searchResults.map((book, index) => (
                  <div 
                    key={`${book.source}-${book.id}-${index}`} 
                    className="book-card"
                    onClick={() => selectBook(book)}
                  >
                    <div className="book-cover">
                      {book.thumbnailUrl ? (
                        <img 
                          src={book.thumbnailUrl} 
                          alt={book.title} 
                          className="book-thumbnail" 
                        />
                      ) : (
                        <div className="placeholder-cover">
                          <span>{book.title.charAt(0)}</span>
                        </div>
                      )}
                    </div>
                    <div className="book-info">
                      <h4>{book.title}</h4>
                      <p>{Array.isArray(book.authors) ? book.authors.join(', ') : book.authors}</p>
                      <span className="source-badge">{book.source}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <>
          <h2>Step 2: Write a Summary</h2>
          
          {selectedBook && (
            <div className="selected-book">
              <button onClick={goBackToSearch} className="back-button">← Back to Search</button>
              
              <div className="book-header">
                {selectedBook.thumbnailUrl && (
                  <img 
                    src={selectedBook.thumbnailUrl} 
                    alt={selectedBook.title} 
                    className="book-thumbnail" 
                  />
                )}
                <div>
                  <h3>{selectedBook.title}</h3>
                  <p>{Array.isArray(selectedBook.authors) ? selectedBook.authors.join(', ') : selectedBook.authors}</p>
                </div>
              </div>
              
              <form onSubmit={submitSummary} className="summary-form">
                <div className="form-group">
                  <label htmlFor="summary">Write a comprehensive summary:</label>
                  <textarea 
                    id="summary"
                    value={summary}
                    onChange={(e) => setSummary(e.target.value)}
                    rows={10}
                    // Continuing src/components/AddBookForm.jsx
                    placeholder="Enter your summary here. Include a short overview, detailed summary, and key takeaways if possible. Try to be accurate and comprehensive."
                    className="summary-textarea"
                    required
                  />
                </div>
                
                <div className="form-actions">
                  <button 
                    type="submit" 
                    disabled={isSubmitting} 
                    className="submit-button"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Summary'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </>
      )}
    </div>
  );
}