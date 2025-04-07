// src/components/BookSummary.jsx
import React, { useState, useEffect } from 'react';

export default function BookSummary({ bookData }) {
  const [currentLanguage, setCurrentLanguage] = useState(bookData.language || 'english');
  const [summary, setSummary] = useState(bookData.summary || '');
  const [isTranslating, setIsTranslating] = useState(false);
  const [availableLanguages, setAvailableLanguages] = useState([]);
  const [error, setError] = useState('');
  
  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  // Fetch available languages for this book
  useEffect(() => {
    const fetchAvailableLanguages = async () => {
      try {
        const response = await fetch(`${API_URL}/api/languages`);
        
        if (response.ok) {
          const data = await response.json();
          setAvailableLanguages(data.languages);
        } else {
          // Fallback to standard languages
          setAvailableLanguages([
            { code: 'english', name: 'English' },
            { code: 'spanish', name: 'Spanish' },
            { code: 'french', name: 'French' },
            { code: 'hindi', name: 'Hindi' },
            { code: 'german', name: 'German' },
            { code: 'italian', name: 'Italian' },
            { code: 'portuguese', name: 'Portuguese' },
            { code: 'russian', name: 'Russian' }
          ]);
        }
      } catch (err) {
        console.error('Error fetching available languages:', err);
        setAvailableLanguages([
          { code: 'english', name: 'English' },
          { code: 'spanish', name: 'Spanish' },
          { code: 'french', name: 'French' },
          { code: 'hindi', name: 'Hindi' }
        ]);
      }
    };

    fetchAvailableLanguages();
  }, []);

  // Handle language change
  const handleLanguageChange = async (e) => {
    const newLanguage = e.target.value;
    
    // If language is the same as current, do nothing
    if (newLanguage === currentLanguage) {
      return;
    }
    
    setIsTranslating(true);
    setError('');
    
    try {
      // Check if summary already exists in this language
      const response = await fetch(`${API_URL}/api/book/summary?title=${encodeURIComponent(bookData.title)}&authors=${encodeURIComponent(bookData.author)}&language=${newLanguage}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch summary');
      }
      
      const data = await response.json();
      setSummary(data.summary);
      setCurrentLanguage(newLanguage);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <div className="book-summary-container">
      {error && <div className="error-message">{error}</div>}
      
      <div className="book-header">
        <div className="book-cover">
          {bookData.thumbnailUrl ? (
            <img 
              src={bookData.thumbnailUrl} 
              alt={bookData.title} 
              className="book-thumbnail" 
            />
          ) : (
            <div className="placeholder-cover">
              <span>{bookData.title.charAt(0)}</span>
            </div>
          )}
        </div>
        
        <div className="book-meta">
          <h1>{bookData.title}</h1>
          <p className="author">By {bookData.author}</p>
          
          {bookData.publishedDate && (
            <p className="published-date">Published: {bookData.publishedDate}</p>
          )}
          
          {bookData.tags && bookData.tags.length > 0 && (
            <div className="tags">
              {bookData.tags.map((tag, index) => (
                <span key={index} className="tag">{tag}</span>
              ))}
            </div>
          )}
          
          {bookData.category && (
            <p className="category">Category: {bookData.category}</p>
          )}
          
          <div className="language-selector">
            <label htmlFor="language-select">Read summary in:</label>
            <select 
              id="language-select"
              value={currentLanguage} 
              onChange={handleLanguageChange}
              disabled={isTranslating}
              className="language-select"
            >
              {availableLanguages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
            {isTranslating && <span className="translating-indicator">Translating...</span>}
          </div>
        </div>
      </div>
      
      <div className="summary-content">
        {isTranslating ? (
          <div className="loading-indicator">Translating summary to {availableLanguages.find(l => l.code === currentLanguage)?.name || currentLanguage}...</div>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: summary.replace(/\n\n/g, '<br><br>') }} />
        )}
      </div>
    </div>
  );
}