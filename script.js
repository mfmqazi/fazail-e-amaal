document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const deedsGrid = document.getElementById('deedsGrid');
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const modal = document.getElementById('deedModal');
    const modalBody = document.getElementById('modalBody');
    const closeModal = document.getElementById('closeModal');
    const navLinks = document.querySelectorAll('.nav-link');

    // Initial Render
    renderDeeds(deeds);

    // Event Listeners
    searchInput.addEventListener('input', handleSearchFilter);
    categoryFilter.addEventListener('change', handleSearchFilter);
    closeModal.addEventListener('click', () => toggleModal(false));

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target.classList.contains('modal-overlay')) {
            toggleModal(false);
        }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            toggleModal(false);
        }
    });

    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            if (targetId.startsWith('#')) {
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    targetSection.scrollIntoView({ behavior: 'smooth' });

                    // Update active link
                    navLinks.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                }
            } else {
                window.location.href = targetId;
            }
        });
    });

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
        }
    });

    // Functions
    function renderDeeds(deedsToRender) {
        deedsGrid.innerHTML = '';

        if (deedsToRender.length === 0) {
            deedsGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-light);">
                    <h3>No deeds found matching your criteria.</h3>
                    <p>Try adjusting your search or filter.</p>
                </div>
            `;
            return;
        }

        deedsToRender.forEach(deed => {
            const card = document.createElement('div');
            card.className = 'deed-card';
            card.innerHTML = `
                <span class="deed-number">Deed #${deed.id}</span>
                <h3 class="deed-title">${deed.title}</h3>
                <p class="deed-preview">${truncateText(deed.description, 100)}</p>
                <div class="deed-tags">
                    <span class="tag">${formatCategory(deed.category)}</span>
                </div>
            `;

            card.addEventListener('click', () => openDeedModal(deed));
            deedsGrid.appendChild(card);
        });
    }

    function handleSearchFilter() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedCategory = categoryFilter.value;

        const filteredDeeds = deeds.filter(deed => {
            const matchesSearch = deed.title.toLowerCase().includes(searchTerm) ||
                deed.description.toLowerCase().includes(searchTerm);
            const matchesCategory = selectedCategory === 'all' || deed.category === selectedCategory;

            return matchesSearch && matchesCategory;
        });

        renderDeeds(filteredDeeds);
    }

    function openDeedModal(deed) {
        modalBody.innerHTML = `
            <div class="modal-header">
                <span class="modal-number">Deed #${deed.id}</span>
                <h2 class="modal-title">${deed.title}</h2>
            </div>
            <div class="modal-body">
                <p>${deed.description}</p>
                <div class="deed-tags">
                    <span class="tag" style="font-size: 1rem; padding: 0.5rem 1rem;">
                        Category: ${formatCategory(deed.category)}
                    </span>
                </div>
            </div>
        `;
        toggleModal(true);
    }

    function toggleModal(show) {
        if (show) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        } else {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    function formatCategory(category) {
        return category.charAt(0).toUpperCase() + category.slice(1);
    }

    function truncateText(text, length) {
        if (text.length <= length) return text;
        return text.substr(0, length) + '...';
    }
});
