// Fazail-e-Amaal Main Script
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const booksGrid = document.getElementById('booksGrid');
    const storiesGrid = document.getElementById('storiesGrid');
    const searchInput = document.getElementById('searchInput');
    const chapterFilter = document.getElementById('chapterFilter');
    const modal = document.getElementById('storyModal');
    const modalBody = document.getElementById('modalBody');
    const closeModal = document.getElementById('closeModal');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const navbar = document.querySelector('.navbar');
    const storiesSection = document.getElementById('stories');

    // State
    let selectedBookId = null;

    // Initialize the page
    init();

    function init() {
        renderBooks();
        renderStories(fazailData.stories);
        populateBookFilter();
        populateChapterFilter();
        setupEventListeners();
        updateStats();
    }

    // Update statistics
    function updateStats() {
        const booksCount = document.getElementById('booksCount');
        const chaptersCount = document.getElementById('chaptersCount');
        const pagesCount = document.getElementById('pagesCount');

        if (booksCount) booksCount.textContent = fazailData.books.length;
        if (chaptersCount) chaptersCount.textContent = fazailData.chapters.length;
        if (pagesCount) pagesCount.textContent = '452';
    }

    // Event Listeners
    function setupEventListeners() {
        // Search and filter
        searchInput.addEventListener('input', handleFilter);
        chapterFilter.addEventListener('change', handleFilter);

        // Modal
        closeModal.addEventListener('click', () => toggleModal(false));
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('modal-overlay')) {
                toggleModal(false);
            }
        });

        // Escape key closes modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                toggleModal(false);
            }
        });

        // Mobile menu
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
        });

        // Close mobile menu when clicking a link
        document.querySelectorAll('.mobile-nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('active');
            });
        });

        // Smooth scrolling for nav links
        document.querySelectorAll('.nav-link, .mobile-nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                if (targetId.startsWith('#')) {
                    const targetSection = document.querySelector(targetId);
                    if (targetSection) {
                        targetSection.scrollIntoView({ behavior: 'smooth' });

                        // Update active link
                        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                        document.querySelectorAll(`.nav-link[href="${targetId}"]`).forEach(l => l.classList.add('active'));
                    }
                }
            });
        });

        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Populate Book Filter
    function populateBookFilter() {
        const bookFilter = document.getElementById('bookFilter');
        bookFilter.innerHTML = '<option value="all">All Books</option>';

        fazailData.books.forEach(book => {
            const option = document.createElement('option');
            option.value = book.id;
            // Use just the book title for the dropdown
            option.textContent = book.title;
            bookFilter.appendChild(option);
        });

        // Add event listener for book filter
        bookFilter.addEventListener('change', (e) => {
            const val = e.target.value;
            if (val === 'all') {
                selectedBookId = null;
                // Remove active from all cards
                document.querySelectorAll('.book-card').forEach(c => c.classList.remove('active'));
                populateChapterFilter(); // Reset to show all chapters
            } else {
                selectedBookId = parseInt(val);
                // Update active card
                document.querySelectorAll('.book-card').forEach(c => {
                    c.classList.remove('active');
                    // Find the card for this book (we can assume order matches index for simplicity or use data attribute)
                });
                // Find and highlight the specific card if it exists in the visible grid
                // Since we render from fazailData, index matches id-1 usually, but let's be safe
                const cards = document.querySelectorAll('.book-card');
                const bookIndex = fazailData.books.findIndex(b => b.id === selectedBookId);
                if (cards[bookIndex]) cards[bookIndex].classList.add('active');

                populateChapterFilter(selectedBookId);
            }

            // Update UI Title
            updateSectionTitle();

            // Reset search and scroll
            searchInput.value = '';
            handleFilter();
        });
    }

    // Update Section Title based on Selected Book
    function updateSectionTitle() {
        const badge = document.querySelector('#stories .section-badge');
        const title = document.querySelector('#stories .section-title');
        const subtitle = document.querySelector('#stories .section-subtitle');

        if (selectedBookId) {
            const book = fazailData.books.find(b => b.id === selectedBookId);
            if (book) {
                // Badge gets Arabic title with proper font
                badge.textContent = book.arabic || 'FAZAIL-E-AMAAL';
                badge.classList.add('arabic-text');
                badge.style.letterSpacing = '0'; // Nastaliq needs 0 letter spacing

                // Title gets English title
                title.textContent = book.title;

                // Subtitle gets description
                subtitle.textContent = book.description;
            }
        } else {
            // Default "All Books" view
            badge.textContent = 'FAZAIL-E-AMAAL';
            badge.classList.remove('arabic-text');
            badge.style.letterSpacing = '1px'; // Reset letter spacing for English

            title.textContent = 'All Stories';
            subtitle.textContent = 'Explore inspiring tales and virtues from all books of Fazail-e-Amaal';
        }

    }

    // Render Books
    function renderBooks() {
        booksGrid.innerHTML = '';

        fazailData.books.forEach((book, index) => {
            const card = document.createElement('div');
            card.className = 'book-card';
            card.style.setProperty('--book-color', book.color);
            card.style.animationDelay = `${index * 0.1}s`;

            // Add active class if this book is selected
            if (selectedBookId === book.id) {
                card.classList.add('active');
            }

            // Count stories for this book
            const storyCount = fazailData.stories.filter(s => s.bookId === book.id).length;

            card.innerHTML = `
                <div class="book-icon">${book.icon}</div>
                <span class="book-number">Book ${book.id}</span>
                <h3 class="book-title">${book.title}</h3>
                <p class="book-arabic">${book.arabic || ''}</p>
                <p class="book-description">${book.description}</p>
                <span class="book-story-count">${storyCount} stories</span>
            `;

            // Make book clickable to filter stories and chapters
            card.addEventListener('click', () => {
                const bookFilter = document.getElementById('bookFilter');

                // Toggle selection
                if (selectedBookId === book.id) {
                    selectedBookId = null;
                    card.classList.remove('active');
                    populateChapterFilter(); // Reset to show all chapters
                    if (bookFilter) bookFilter.value = 'all';
                } else {
                    // Remove active from all cards
                    document.querySelectorAll('.book-card').forEach(c => c.classList.remove('active'));
                    selectedBookId = book.id;
                    card.classList.add('active');
                    populateChapterFilter(book.id); // Filter chapters for this book
                    if (bookFilter) bookFilter.value = book.id;
                }

                // Update Title
                updateSectionTitle();

                // Reset search and scroll
                searchInput.value = '';

                // Filter stories and scroll to stories section, forcing refresh of view
                handleFilter();
                storiesSection.scrollIntoView({ behavior: 'smooth' });
            });

            booksGrid.appendChild(card);
        });
    }

    // Render Stories
    function renderStories(storiesToRender) {
        storiesGrid.innerHTML = '';

        if (storiesToRender.length === 0) {
            storiesGrid.innerHTML = `
                <div class="empty-state">
                    <h3>No stories found</h3>
                    <p>Select another book or adjust your search.</p>
                </div>
            `;
            return;
        }

        storiesToRender.forEach((story, index) => {
            const card = document.createElement('div');
            card.className = 'story-card';
            card.style.animationDelay = `${index * 0.05}s`;

            // Get book info for this story
            const book = fazailData.books.find(b => b.id === story.bookId);
            const bookTitle = book ? book.title : '';

            card.innerHTML = `
                <span class="story-chapter">${story.chapter}</span>
                <h3 class="story-title">${story.title}</h3>
                <p class="story-preview">${truncateText(stripHtml(story.preview), 150)}</p>
                <div class="story-footer">
                    <span class="story-book-tag">${bookTitle}</span>
                    <span class="story-read-more">
                        Read Story
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </span>
                </div>
            `;

            card.addEventListener('click', () => openStoryModal(story));
            storiesGrid.appendChild(card);
        });
    }

    // Strip HTML tags
    function stripHtml(html) {
        const tmp = document.createElement('div');
        tmp.innerHTML = html;
        return tmp.textContent || tmp.innerText || '';
    }

    // Populate Chapter Filter
    function populateChapterFilter(bookId = null) {
        // Clear existing options except 'All Chapters'
        chapterFilter.innerHTML = '<option value="all">All Chapters</option>';

        let chaptersToShow = fazailData.chapters;

        // Filter chapters if a book is selected
        if (bookId) {
            chaptersToShow = fazailData.chapters.filter(chapter => chapter.bookId === bookId);
        }

        chaptersToShow.forEach(chapter => {
            const option = document.createElement('option');
            option.value = chapter.title;
            // Show Arabic title if available
            option.textContent = chapter.title + (chapter.arabic ? ' (' + chapter.arabic + ')' : '');
            chapterFilter.appendChild(option);
        });
    }

    // Handle Filter
    function handleFilter() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedChapter = chapterFilter.value;

        const filteredStories = fazailData.stories.filter(story => {
            const matchesSearch = story.title.toLowerCase().includes(searchTerm) ||
                stripHtml(story.preview).toLowerCase().includes(searchTerm) ||
                stripHtml(story.content).toLowerCase().includes(searchTerm);
            const matchesChapter = selectedChapter === 'all' || story.chapter === selectedChapter;
            const matchesBook = selectedBookId === null || story.bookId === selectedBookId;

            return matchesSearch && matchesChapter && matchesBook;
        });

        renderStories(filteredStories);
    }

    // Open Story Modal
    function openStoryModal(story) {
        // Get book info
        const book = fazailData.books.find(b => b.id === story.bookId);
        const bookTitle = book ? book.title : '';

        modalBody.innerHTML = `
            <div class="modal-header">
                <span class="modal-book-title">${bookTitle}</span>
                <span class="modal-chapter">${story.chapter}</span>
                <h2 class="modal-title">${story.title}</h2>
            </div>
            <div class="modal-content-body">
                ${formatContent(story.content)}
            </div>
        `;

        toggleModal(true);
    }

    // Format Content - handles Arabic text and paragraphs
    function formatContent(text) {
        if (!text) return '';

        // Text already has HTML from the extraction, just clean up
        let formatted = text;

        // Handle paragraph breaks
        formatted = formatted.split('\n\n').map(para => {
            const trimmed = para.trim();
            if (!trimmed) return '';

            // If already wrapped in a tag, return as is
            if (trimmed.startsWith('<')) return trimmed;

            // Check if it's a quote
            if ((trimmed.startsWith('"') && trimmed.endsWith('"')) ||
                (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
                return `<blockquote class="story-quote">${trimmed}</blockquote>`;
            }

            return `<p>${trimmed}</p>`;
        }).join('');

        return formatted;
    }

    // Toggle Modal
    function toggleModal(show) {
        if (show) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // Truncate Text
    function truncateText(text, length) {
        if (!text) return '';
        if (text.length <= length) return text;
        return text.substr(0, length).trim() + '...';
    }

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe cards after they're rendered
    setTimeout(() => {
        document.querySelectorAll('.book-card, .story-card').forEach(card => {
            observer.observe(card);
        });
    }, 100);
});

