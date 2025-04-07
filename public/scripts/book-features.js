// book-features.js - Comprehensive solution for book summary page functionality
document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ Book features JS loaded");
  
  // Global variables
  const searchInput = document.getElementById("search");
  const postList = document.getElementById("postList");
  const noResults = document.getElementById("noResults");
  const sortOptions = document.getElementById("sortOptions");
  const randomBtn = document.getElementById("randomBook");
  const clearFiltersBtn = document.getElementById("clearFiltersBtn");
  const topRatedBtn = document.getElementById("topRatedBtn");
  const bookmarksBtn = document.getElementById("bookmarksBtn");
  const leaderboardBtn = document.getElementById("leaderboardBtn");
  const bookmarksModal = document.getElementById("bookmarksModal");
  const leaderboardModal = document.getElementById("leaderboardModal");
  const closeBookmarks = document.getElementById("closeBookmarks");
  const closeLeaderboard = document.getElementById("closeLeaderboard");
  const exportBookmarks = document.getElementById("exportBookmarks");
  
  // Initialize all features
  initializeUserStats();
  initializeBookmarks();
  initializeFilterUI();
  setupEventListeners();
  
  // Set up all event listeners
  function setupEventListeners() {
    // Search functionality
    if (searchInput) {
      searchInput.addEventListener("input", filterPosts);
    }
    
    // Sort dropdown
    if (sortOptions) {
      sortOptions.addEventListener("change", sortPosts);
    }
    
    // Random book button
    if (randomBtn) {
      randomBtn.addEventListener("click", selectRandomBook);
    }
    
    // Top rated button
    if (topRatedBtn) {
      topRatedBtn.addEventListener("click", showTopRated);
    }
    
    // Clear filters
    if (clearFiltersBtn) {
      clearFiltersBtn.addEventListener("click", clearFilters);
    }
    
    // Tags for filtering
    document.querySelectorAll(".tag").forEach(tag => {
      tag.addEventListener("click", (e) => {
        e.preventDefault();
        const tagValue = tag.getAttribute("data-tag");
        filterByTag(tagValue);
      });
    });
    
    // Category filter buttons
    document.querySelectorAll(".category-filter").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const tagValue = btn.getAttribute("data-tag");
        filterByTag(tagValue);
      });
    });
    
    // Author filter buttons
    document.querySelectorAll(".author-filter").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const authorValue = btn.getAttribute("data-author");
        filterByAuthor(authorValue);
      });
    });
    
    // Bookmark buttons
    document.querySelectorAll(".bookmark-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const slug = btn.getAttribute("data-slug");
        toggleBookmark(slug, btn);
      });
    });
    
    // Read status buttons
    document.querySelectorAll(".read-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const slug = btn.getAttribute("data-slug");
        toggleReadStatus(slug, btn);
      });
    });
    
    // Rating stars
    document.querySelectorAll(".star").forEach(star => {
      star.addEventListener("click", (e) => {
        e.preventDefault();
        const rating = parseInt(star.getAttribute("data-rating"));
        const slug = star.getAttribute("data-slug");
        submitRating(slug, rating);
      });
    });
    
    // Bookmarks modal
    if (bookmarksBtn && bookmarksModal) {
      bookmarksBtn.addEventListener("click", () => {
        renderBookmarksList();
        bookmarksModal.style.display = "flex";
      });
    }
    
    if (closeBookmarks && bookmarksModal) {
      closeBookmarks.addEventListener("click", () => {
        bookmarksModal.style.display = "none";
      });
    }
    
    if (bookmarksModal) {
      bookmarksModal.addEventListener("click", (e) => {
        if (e.target === bookmarksModal) {
          bookmarksModal.style.display = "none";
        }
      });
    }
    
    if (exportBookmarks) {
      exportBookmarks.addEventListener("click", exportBookmarksList);
    }
    
    // Leaderboard modal
    if (leaderboardBtn && leaderboardModal) {
      leaderboardBtn.addEventListener("click", () => {
        populateLeaderboard();
        leaderboardModal.style.display = "flex";
      });
    }
    
    if (closeLeaderboard && leaderboardModal) {
      closeLeaderboard.addEventListener("click", () => {
        leaderboardModal.style.display = "none";
      });
    }
    
    if (leaderboardModal) {
      leaderboardModal.addEventListener("click", (e) => {
        if (e.target === leaderboardModal) {
          leaderboardModal.style.display = "none";
        }
      });
    }
  }
  
  // CORE FUNCTIONALITY
  
  // Search and filtering
  function filterPosts() {
    const query = searchInput.value.toLowerCase();
    let visibleCount = 0;
    
    document.querySelectorAll(".post-item").forEach(item => {
      const title = item.getAttribute("data-title") || "";
      const description = item.getAttribute("data-description") || "";
      const tags = item.getAttribute("data-tags") || "";
      const author = item.getAttribute("data-author")?.toLowerCase() || "";
      
      const match = title.includes(query) || 
                   description.includes(query) || 
                   tags.includes(query) ||
                   author.includes(query);
      
      item.style.display = match ? "" : "none";
      if (match) visibleCount++;
    });
    
    if (noResults) {
      noResults.style.display = visibleCount === 0 ? "block" : "none";
    }
  }
  
  function filterByTag(tag) {
    let visibleCount = 0;
    
    document.querySelectorAll(".post-item").forEach(item => {
      const tags = (item.getAttribute("data-tags") || "").toLowerCase();
      const shouldShow = tags.includes(tag.toLowerCase());
      item.style.display = shouldShow ? '' : 'none';
      if (shouldShow) visibleCount++;
    });
    
    document.querySelectorAll(".tag, .category-filter").forEach(el => {
      el.classList.toggle("active-tag", el.getAttribute("data-tag") === tag);
    });
    
    if (noResults) {
      noResults.style.display = visibleCount === 0 ? "block" : "none";
    }
  }
  
  function filterByAuthor(author) {
    let visibleCount = 0;
    
    document.querySelectorAll(".post-item").forEach(item => {
      const shouldShow = item.getAttribute("data-author") === author;
      item.style.display = shouldShow ? '' : 'none';
      if (shouldShow) visibleCount++;
    });
    
    document.querySelectorAll(".author-filter").forEach(btn => {
      btn.classList.toggle("active-tag", btn.getAttribute("data-author") === author);
    });
    
    if (noResults) {
      noResults.style.display = visibleCount === 0 ? "block" : "none";
    }
  }
  
  function sortPosts() {
    if (!sortOptions || !postList) return;
    
    const sortBy = sortOptions.value;
    const items = Array.from(postList.children);
    
    const sorted = items.sort((a, b) => {
      if (sortBy === 'popular') {
        return parseInt(b.dataset.views) - parseInt(a.dataset.views);
      }
      if (sortBy === 'oldest') {
        return new Date(a.dataset.date) - new Date(b.dataset.date);
      }
      if (sortBy === 'rated') {
        const ratingA = parseFloat(a.dataset.rating) || 0;
        const ratingB = parseFloat(b.dataset.rating) || 0;
        const countA = parseInt(a.dataset.ratingCount) || 0;
        const countB = parseInt(b.dataset.ratingCount) || 0;
        
        // If ratings are the same or both have less than 3 ratings, sort by views
        if (ratingA === ratingB || (countA < 3 && countB < 3)) {
          return parseInt(b.dataset.views) - parseInt(a.dataset.views);
        }
        
        // If one has less than 3 ratings, prioritize the one with more
        if (countA < 3) return 1;
        if (countB < 3) return -1;
        
        return ratingB - ratingA;
      }
      return new Date(b.dataset.date) - new Date(a.dataset.date); // newest by default
    });
    
    // Clear and re-append all items
    while (postList.firstChild) {
      postList.removeChild(postList.firstChild);
    }
    
    sorted.forEach(el => postList.appendChild(el));
    
    // Check if we need to show "no results" after sorting
    checkNoResults();
  }
  
  function selectRandomBook() {
    const postSlugs = window.postSlugs || [];
    if (postSlugs.length > 0) {
      const randomUrl = postSlugs[Math.floor(Math.random() * postSlugs.length)];
      if (randomUrl) window.location.href = randomUrl;
    }
  }
  
  function showTopRated() {
    if (sortOptions) {
      sortOptions.value = "rated";
      sortPosts();
    }
  }
  
  function clearFilters() {
    // Reset search box
    if (searchInput) searchInput.value = "";
    
    // Show all items
    document.querySelectorAll(".post-item").forEach(item => {
      item.style.display = '';
    });
    
    // Remove active class from all filter buttons
    document.querySelectorAll(".tag, .author-filter, .category-filter").forEach(el => {
      el.classList.remove("active-tag");
    });
    
    // Reset advanced filter UI
    document.querySelectorAll(".filter-option").forEach(opt => opt.classList.remove("selected"));
    showFilterStep("Language");
    
    // Clear filter preferences
    window.selectedLanguage = null;
    window.selectedType = null;
    window.selectedCategory = null;
    window.selectedSubcategory = null;
    localStorage.removeItem("bookFilter");
    
    // Hide no results message
    if (noResults) {
      noResults.style.display = 'none';
    }
  }
  
  function checkNoResults() {
    if (!noResults) return;
    
    // Count visible items
    const visibleItems = Array.from(document.querySelectorAll(".post-item"))
      .filter(item => item.style.display !== 'none').length;
    
    // Show/hide no results message
    noResults.style.display = visibleItems === 0 ? 'block' : 'none';
  }
  
  // BOOKMARKS FUNCTIONALITY
  
  function initializeBookmarks() {
    const bookmarks = getBookmarks();
    
    // Update UI to reflect bookmarked status
    document.querySelectorAll(".bookmark-btn").forEach(btn => {
      const slug = btn.getAttribute("data-slug");
      if (bookmarks.includes(slug)) {
        btn.classList.add("active");
      }
    });
  }
  
  function getBookmarks() {
    try {
      const bookmarksJSON = localStorage.getItem("bookmarks");
      return bookmarksJSON ? JSON.parse(bookmarksJSON) : [];
    } catch (e) {
      console.error("Error getting bookmarks:", e);
      return [];
    }
  }
  
  function toggleBookmark(slug, button) {
    // Get current bookmarks
    let bookmarks = getBookmarks();
    const userStats = getUserStats();
    let pointsAwarded = false;
    
    // Toggle bookmark status
    if (bookmarks.includes(slug)) {
      // Remove from bookmarks
      bookmarks = bookmarks.filter(id => id !== slug);
      button.classList.remove("active");
    } else {
      // Add to bookmarks
      bookmarks.push(slug);
      button.classList.add("active");
      
      // Award points for first time bookmarking if not already tracked
      if (!userStats.bookmarks || !userStats.bookmarks.includes(slug)) {
        awardPoints(5, 'bookmark');
        pointsAwarded = true;
        
        // Track bookmarked item
        if (!userStats.bookmarks) userStats.bookmarks = [];
        userStats.bookmarks.push(slug);
        saveUserStats(userStats);
      }
    }
    
    // Save to localStorage
    localStorage.setItem("bookmarks", JSON.stringify(bookmarks));
    
    // Show notification if points awarded
    if (pointsAwarded) {
      showNotification("🎉 +5 points for bookmarking!");
    }
  }
  
  function renderBookmarksList() {
    const bookmarksList = document.getElementById("bookmarksList");
    if (!bookmarksList) return;
    
    const bookmarks = getBookmarks();
    
    // Clear existing content
    bookmarksList.innerHTML = "";
    
    if (bookmarks.length === 0) {
      bookmarksList.innerHTML = `<div class="empty-bookmarks">You haven't bookmarked any book summaries yet.</div>`;
      return;
    }
    
    // Create a list of bookmarked books from the DOM
    const bookmarkedPosts = [];
    
    // Loop through all posts and find the bookmarked ones
    document.querySelectorAll(".post-item").forEach(item => {
      const slug = item.getAttribute("data-slug");
      if (bookmarks.includes(slug)) {
        const titleEl = item.querySelector("h3");
        const authorEl = item.querySelector(".author");
        
        bookmarkedPosts.push({
          id: slug,
          title: titleEl ? titleEl.textContent : "Unknown Title",
          author: authorEl ? authorEl.textContent.replace("By ", "") : "",
          date: item.getAttribute("data-date")
        });
      }
    });
    
    const list = document.createElement("ul");
    list.style.display = "block"; // Override flex display for this list
    
    bookmarkedPosts.forEach(post => {
      const item = document.createElement("li");
      item.innerHTML = `
        <h3><a href="/books/${post.id}/">${post.title}</a></h3>
        ${post.author ? `<p class="author">By ${post.author}</p>` : ''}
        <p class="date">${new Date(post.date).toLocaleDateString()}</p>
        <button class="remove-bookmark" data-slug="${post.id}">Remove</button>
      `;
      list.appendChild(item);
    });
    
    bookmarksList.appendChild(list);
    
    // Add event listeners to remove buttons
    document.querySelectorAll(".remove-bookmark").forEach(btn => {
      btn.addEventListener("click", () => {
        const slug = btn.getAttribute("data-slug");
        // Remove from bookmarks
        let bookmarks = getBookmarks().filter(id => id !== slug);
        localStorage.setItem("bookmarks", JSON.stringify(bookmarks));
        
        // Update UI
        document.querySelectorAll(`.bookmark-btn[data-slug="${slug}"]`).forEach(bookmarkBtn => {
          bookmarkBtn.classList.remove("active");
        });
        
        renderBookmarksList();
      });
    });
  }
  
  function exportBookmarksList() {
    const bookmarks = getBookmarks();
    
    if (bookmarks.length === 0) {
      alert("You don't have any bookmarked summaries to export.");
      return;
    }
    
    // Get bookmarked books
    const bookmarkedPosts = [];
    
    // Loop through all posts and find the bookmarked ones
    document.querySelectorAll(".post-item").forEach(item => {
      const slug = item.getAttribute("data-slug");
      if (bookmarks.includes(slug)) {
        const titleEl = item.querySelector("h3");
        const authorEl = item.querySelector(".author");
        
        bookmarkedPosts.push({
          title: titleEl ? titleEl.textContent : "Unknown Title",
          author: authorEl ? authorEl.textContent.replace("By ", "") : ""
        });
      }
    });
    
    // Format the list as text
    let exportText = "# My Bookmarked Book Summaries\n\n";
    
    bookmarkedPosts.forEach(post => {
      exportText += `- ${post.title}${post.author ? ` by ${post.author}` : ''}\n`;
    });
    
    // Create download link
    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'my_bookmarked_summaries.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
  
  // USER STATS AND GAMIFICATION
  
  function initializeUserStats() {
    // Get user stats from localStorage
    const userStats = getUserStats();
    
    // Update UI with user stats
    const pointsEl = document.getElementById("userPointsValue");
    const booksReadEl = document.getElementById("userBooksRead");
    const progressBar = document.getElementById("userProgressBar");
    const badgesContainer = document.getElementById("userBadges");
    
    if (pointsEl) pointsEl.textContent = userStats.points;
    if (booksReadEl) booksReadEl.textContent = userStats.booksRead;
    
    // Update progress bar - assuming 1000 points is max
    if (progressBar) {
      const progressPercent = Math.min(100, (userStats.points / 1000) * 100);
      progressBar.style.width = `${progressPercent}%`;
    }
    
    // Update badges
    if (badgesContainer) {
      badgesContainer.innerHTML = '';
      
      // Generate badges based on achievements
      const badges = generateBadges(userStats);
      
      badges.forEach(badge => {
        const badgeElement = document.createElement("span");
        badgeElement.className = "badge-tooltip";
        badgeElement.setAttribute("data-tooltip", badge.name);
        
        const badgeIcon = document.createElement("span");
        badgeIcon.className = "badge";
        badgeIcon.innerHTML = badge.icon;
        
        badgeElement.appendChild(badgeIcon);
        badgesContainer.appendChild(badgeElement);
      });
    }
    
    // Initialize read status for books
    updateReadStatusUI();
  }
  
  function getUserStats() {
    try {
      // Get stats from localStorage
      const statsJSON = localStorage.getItem("userStats");
      if (statsJSON) {
        return JSON.parse(statsJSON);
      }
    } catch (e) {
      console.error("Error getting user stats:", e);
    }
    
    // Default stats
    return {
      points: 0,
      booksRead: 0,
      booksBookmarked: 0,
      ratingsGiven: 0,
      readBooks: []
    };
  }
  
  function saveUserStats(stats) {
    try {
      localStorage.setItem("userStats", JSON.stringify(stats));
    } catch (e) {
      console.error("Error saving user stats:", e);
    }
  }
  
  function generateBadges(userStats) {
    const badges = [];
    
    // Reader badges
    if (userStats.booksRead >= 1) {
      badges.push({ name: "First Book Read", icon: "📚" });
    }
    if (userStats.booksRead >= 5) {
      badges.push({ name: "Bookworm", icon: "🐛" });
    }
    if (userStats.booksRead >= 10) {
      badges.push({ name: "Avid Reader", icon: "📖" });
    }
    if (userStats.booksRead >= 25) {
      badges.push({ name: "Book Master", icon: "🏆" });
    }
    
    // Points badges
    if (userStats.points >= 100) {
      badges.push({ name: "Century Club", icon: "💯" });
    }
    if (userStats.points >= 500) {
      badges.push({ name: "Scholar", icon: "🧠" });
    }
    if (userStats.points >= 1000) {
      badges.push({ name: "Intellectual", icon: "🎓" });
    }
    
    // Activity badges
    if (userStats.booksBookmarked >= 5) {
      badges.push({ name: "Curator", icon: "🔖" });
    }
    if (userStats.ratingsGiven >= 10) {
      badges.push({ name: "Critic", icon: "⭐" });
    }
    
    return badges;
  }
  
  function awardPoints(points, activity) {
    const userStats = getUserStats();
    
    userStats.points += points;
    
    // Track specific activities
    switch (activity) {
      case 'read':
        userStats.booksRead += 1;
        break;
      case 'bookmark':
        userStats.booksBookmarked = (userStats.booksBookmarked || 0) + 1;
        break;
      case 'rate':
        userStats.ratingsGiven = (userStats.ratingsGiven || 0) + 1;
        break;
    }
    
    saveUserStats(userStats);
    initializeUserStats(); // Refresh UI
  }
  
  function toggleReadStatus(slug, button) {
    const userStats = getUserStats();
    
    if (!userStats.readBooks) {
      userStats.readBooks = [];
    }
    
    if (userStats.readBooks.includes(slug)) {
      // Remove from read books
      userStats.readBooks = userStats.readBooks.filter(id => id !== slug);
      button.textContent = "Mark Read";
      button.classList.remove("read");
      
      // Reduce points - don't go below 0
      userStats.points = Math.max(0, userStats.points - 10);
      userStats.booksRead = Math.max(0, userStats.booksRead - 1);
    } else {
      // Add to read books
      userStats.readBooks.push(slug);
      button.textContent = "Read";
      button.classList.add("read");
      
      // Award points
      userStats.points += 10;
      userStats.booksRead += 1;
      
      // Show achievements notification if badge earned
      const oldBadges = generateBadges({...userStats, points: userStats.points - 10, booksRead: userStats.booksRead - 1});
      const newBadges = generateBadges(userStats);
      
      if (newBadges.length > oldBadges.length) {
        // New badge earned
        const newBadge = newBadges[newBadges.length - 1];
        showNotification(`🎉 Achievement Unlocked: ${newBadge.name} ${newBadge.icon}`);
      } else {
        showNotification("🎉 +10 points for reading!");
      }
    }
    
    saveUserStats(userStats);
    initializeUserStats(); // Refresh UI
  }
  
  function updateReadStatusUI() {
    const userStats = getUserStats();
    
    if (!userStats.readBooks) {
      return;
    }
    
    document.querySelectorAll(".read-btn").forEach(button => {
      const slug = button.getAttribute("data-slug");
      if (userStats.readBooks.includes(slug)) {
        button.textContent = "Read";
        button.classList.add("read");
      } else {
        button.textContent = "Mark Read";
        button.classList.remove("read");
      }
    });
  }
  
  function showNotification(message) {
    // Create notification element
    const notification = document.createElement("div");
    notification.style.position = "fixed";
    notification.style.bottom = "20px";
    notification.style.right = "20px";
    notification.style.backgroundColor = "#4CAF50";
    notification.style.color = "white";
    notification.style.padding = "12px 24px";
    notification.style.borderRadius = "4px";
    notification.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
    notification.style.zIndex = "1000";
    notification.style.transition = "opacity 0.5s";
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.opacity = "0";
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 500);
    }, 3000);
  }
  
  // RATING FUNCTIONALITY
  
  function submitRating(slug, rating) {
    // Get all stars for this book
    const starsContainer = document.querySelector(`.rating-display[data-slug="${slug}"] .stars`);
    if (!starsContainer) return;
    
    const stars = starsContainer.querySelectorAll('.star');
    
    // Update UI to show the new rating
    stars.forEach((star, index) => {
      if (index < rating) {
        star.textContent = '★';
      } else {
        star.textContent = '☆';
      }
    });
    
    // Update the display of average rating
    const ratingDisplay = starsContainer.nextElementSibling;
    const countDisplay = ratingDisplay.nextElementSibling;
    
    // Simple client-side implementation
    const currentItem = document.querySelector(`.post-item[data-slug="${slug}"]`);
    if (currentItem) {
      const currentRating = parseFloat(currentItem.getAttribute('data-rating')) || 0;
      const currentCount = parseInt(currentItem.getAttribute('data-rating-count')) || 0;
      
      let newCount, newAverage;
      
      // If it's the first rating
      if (currentCount === 0) {
        newCount = 1;
        newAverage = rating;
      } else {
        // Simple average calculation
        newCount = currentCount + 1;
        newAverage = ((currentRating * currentCount) + rating) / newCount;
      }
      
      // Update the displays
      ratingDisplay.textContent = newAverage.toFixed(1);
      countDisplay.textContent = `(${newCount} ratings)`;
      
      // Update the data attributes
      currentItem.setAttribute('data-rating', newAverage);
      currentItem.setAttribute('data-rating-count', newCount);
      
      // Award points for rating
      const userStats = getUserStats();
      
      // Check if user has already rated this book
      if (!userStats.ratings) userStats.ratings = {};
      
      if (!userStats.ratings[slug]) {
        userStats.ratings[slug] = rating;
        awardPoints(3, 'rate');
        showNotification("🎉 +3 points for rating!");
      } else {
        // User is updating their rating
        userStats.ratings[slug] = rating;
      }
      
      saveUserStats(userStats);
    }
  }
  
  // LEADERBOARD FUNCTIONALITY
  
  async function fetchLeaderboard() {
    const SUPABASE_URL = window.SUPABASE_URL;
    const SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY;
    
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
      return [];
    }
    
    try {
      const res = await fetch(`${SUPABASE_URL}/rest/v1/user_points?order=points.desc&limit=10`, {
        headers: {
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${SUPABASE_ANON_KEY}`
        }
      });
      const data = await res.json();
      return Array.isArray(data) ? data : [];
    } catch (e) {
      console.error("Error fetching leaderboard", e);
      return [];
    }
  }
  
  async function populateLeaderboard() {
    const leaderboardBody = document.getElementById("leaderboardBody");
    if (!leaderboardBody) return;
    
    try {
      // Start with loading indicator
      leaderboardBody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; padding: 1rem;">
            Loading leaderboard data...
          </td>
        </tr>
      `;
      
      // Try to fetch real data, or use mock data if fetch fails
      let data = [];
      try {
        data = await fetchLeaderboard();
      } catch (error) {
        console.error("Error fetching leaderboard data:", error);
      }
      
      // If we got data, use it, otherwise use mock data
      if (data && data.length > 0) {
        // Clear previous content
        leaderboardBody.innerHTML = "";
        
        // Add each user to the leaderboard
        data.forEach((user, index) => {
          const badges = user.badges || [];
          const badgesHtml = Array.isArray(badges) ? badges.map(badge => 
            `<span class="badge-tooltip" data-tooltip="${badge.name || ''}">
              <span class="badge">${badge.icon || '🏅'}</span>
            </span>`
          ).join('') : '';
          
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${index + 1}</td>
            <td>${user.username || 'Anonymous Reader'}</td>
            <td>${user.books_read || 0}</td>
            <td>${user.points || 0}</td>
            <td>${badgesHtml || ''}</td>
          `;
          
          leaderboardBody.appendChild(row);
        });
      } else {
        // If no data, add some mock data
        addMockLeaderboardData();
      }
    } catch (error) {
      console.error("Error populating leaderboard:", error);
      // If error, add mock data
      addMockLeaderboardData();
    }
  }
  
  function addMockLeaderboardData() {
    const leaderboardBody = document.getElementById("leaderboardBody");
    if (!leaderboardBody) return;
    
    leaderboardBody.innerHTML = ""; // Clear loading indicator
    
    const mockData = [
      { username: "BookMaster", books_read: 42, points: 950, badges: [{ name: "Intellectual", icon: "🎓" }, { name: "Book Master", icon: "🏆" }] },
      { username: "LiteraryExplorer", books_read: 36, points: 780, badges: [{ name: "Scholar", icon: "🧠" }, { name: "Avid Reader", icon: "📖" }] },
      { username: "Bibliophile", books_read: 28, points: 620, badges: [{ name: "Century Club", icon: "💯" }, { name: "Curator", icon: "🔖" }] },
      { username: "PageTurner", books_read: 23, points: 540, badges: [{ name: "Critic", icon: "⭐" }] },
      { username: "Bookworm", books_read: 19, points: 470, badges: [{ name: "Bookworm", icon: "🐛" }] },
      { username: "KnowledgeSeeker", books_read: 15, points: 380, badges: [{ name: "First Book Read", icon: "📚" }] },
      { username: "WordSmith", books_read: 12, points: 320 },
      { username: "LitLover", books_read: 10, points: 280 },
      { username: "ReadingRookie", books_read: 7, points: 220 },
      { username: "NovelNewbie", books_read: 4, points: 160 }
    ];
    
    mockData.forEach((user, index) => {
      const badges = user.badges || [];
      const badgesHtml = badges.map(badge => 
        `<span class="badge-tooltip" data-tooltip="${badge.name}">
          <span class="badge">${badge.icon}</span>
        </span>`
      ).join('');
      
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${index + 1}</td>
        <td>${user.username}</td>
        <td>${user.books_read}</td>
        <td>${user.points}</td>
        <td>${badgesHtml}</td>
      `;
      
      leaderboardBody.appendChild(row);
    });