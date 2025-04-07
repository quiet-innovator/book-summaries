// Add this function to src/components/BookList.jsx
const fetchAvailableLanguages = async (bookId) => {
  try {
    const response = await fetch(`${API_URL}/api/book/available-languages?id=${bookId}`);
    if (response.ok) {
      const data = await response.json();
      return data.languages;
    }
    return ['english']; // Default to English only
  } catch (error) {
    console.error('Error fetching available languages:', error);
    return ['english']; // Default to English only
  }
};

// Then update your book card rendering to include language badges
// Inside the map function that renders books:
{books.map((book, index) => {
  const [languages, setLanguages] = useState(['english']);
  
  useEffect(() => {
    const getLanguages = async () => {
      const availableLanguages = await fetchAvailableLanguages(book.id);
      setLanguages(availableLanguages);
    };
    getLanguages();
  }, [book.id]);
  
  return (
    <div 
      key={`${book.source || 'local'}-${book.id}-${index}`} 
      className="book-card"
      onClick={() => handleSelectBook(book)}
    >
      {/* ... Rest of your book card JSX ... */}
      
      {/* Add language badges */}
      {languages.length > 1 && (
        <div className="language-badges">
          {languages.map(lang => (
            <span key={lang} className="language-badge">
              {lang === 'english' ? '🇬🇧' : 
               lang === 'spanish' ? '🇪🇸' : 
               lang === 'french' ? '🇫🇷' : '🇮🇳'}
            </span>
          ))}
        </div>
      )}
    </div>
  );
})}