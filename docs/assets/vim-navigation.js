/**
 * Vim-like Keyboard Navigation for MkDocs
 *
 * Keybindings:
 *   j/k        - Scroll down/up (smooth)
 *   d/u        - Scroll down/up by half page (like Ctrl-d/Ctrl-u in vim)
 *   gg         - Jump to top of page
 *   G          - Jump to bottom of page
 *   h/l        - Navigate to previous/next page
 *   /          - Focus search box (if available)
 *   Escape     - Blur active element (exit input focus)
 */

(function() {
  'use strict';

  // Configuration
  const config = {
    scrollStep: 60,              // pixels for j/k
    scrollSmooth: true,          // enable smooth scrolling
    enableInInputs: false,       // allow vim keys while typing (usually false)
  };

  // State
  let ggBuffer = false;          // track 'g' press for 'gg' command
  let ggTimeout = null;

  /**
   * Check if user is currently in an input field
   */
  function isTyping() {
    const active = document.activeElement;
    const tag = active?.tagName?.toLowerCase();
    return (
      tag === 'input' ||
      tag === 'textarea' ||
      tag === 'select' ||
      active?.isContentEditable
    );
  }

  /**
   * Smooth scroll helper
   */
  function scrollBy(amount) {
    if (config.scrollSmooth) {
      window.scrollBy({ top: amount, behavior: 'smooth' });
    } else {
      window.scrollBy(0, amount);
    }
  }

  /**
   * Scroll to position
   */
  function scrollTo(position) {
    if (config.scrollSmooth) {
      window.scrollTo({ top: position, behavior: 'smooth' });
    } else {
      window.scrollTo(0, position);
    }
  }

  /**
   * Find previous/next page links
   * Tries multiple selectors for different MkDocs themes
   */
  function findNavLinks() {
    const selectors = {
      prev: [
        'a[rel="prev"]',
        '.md-footer__link--prev',
        'a.prev-page',
        'nav .previous a',
        'a[title*="Previous"]',
        'a:has(.icon-previous)',
      ],
      next: [
        'a[rel="next"]',
        '.md-footer__link--next',
        'a.next-page',
        'nav .next a',
        'a[title*="Next"]',
        'a:has(.icon-next)',
      ]
    };

    const prev = selectors.prev.map(s => document.querySelector(s)).find(el => el);
    const next = selectors.next.map(s => document.querySelector(s)).find(el => el);

    return { prev, next };
  }

  /**
   * Focus search input
   */
  function focusSearch() {
    const searchSelectors = [
      'input[type="search"]',
      'input[name="query"]',
      '#mkdocs-search-query',
      '.search-input',
      '[data-search-input]',
    ];

    for (const selector of searchSelectors) {
      const input = document.querySelector(selector);
      if (input) {
        input.focus();
        input.select();
        return true;
      }
    }
    return false;
  }

  /**
   * Main keyboard handler
   */
  function handleKeyPress(e) {
    // Allow normal behavior in input fields (unless explicitly enabled)
    if (!config.enableInInputs && isTyping()) {
      // Still allow Escape to blur
      if (e.key === 'Escape') {
        document.activeElement.blur();
        e.preventDefault();
      }
      return;
    }

    const key = e.key;

    // Handle 'gg' (go to top) - requires two 'g' presses
    if (key === 'g') {
      if (ggBuffer) {
        // Second 'g' press - go to top
        scrollTo(0);
        ggBuffer = false;
        clearTimeout(ggTimeout);
        e.preventDefault();
        return;
      } else {
        // First 'g' press - wait for second one
        ggBuffer = true;
        ggTimeout = setTimeout(() => {
          ggBuffer = false;
        }, 1000); // 1 second timeout
        e.preventDefault();
        return;
      }
    }

    // Clear gg buffer on any other key
    if (ggBuffer && key !== 'g') {
      ggBuffer = false;
      clearTimeout(ggTimeout);
    }

    // Single key commands
    switch(key) {
      case 'j':
        // Scroll down
        scrollBy(config.scrollStep);
        e.preventDefault();
        break;

      case 'k':
        // Scroll up
        scrollBy(-config.scrollStep);
        e.preventDefault();
        break;

      case 'd':
        // Scroll down half page (like Ctrl-d)
        scrollBy(window.innerHeight / 2);
        e.preventDefault();
        break;

      case 'u':
        // Scroll up half page (like Ctrl-u)
        scrollBy(-window.innerHeight / 2);
        e.preventDefault();
        break;

      case 'G':
        // Go to bottom (capital G)
        scrollTo(document.documentElement.scrollHeight);
        e.preventDefault();
        break;

      case 'h':
        // Previous page
        const { prev } = findNavLinks();
        if (prev) {
          prev.click();
          e.preventDefault();
        }
        break;

      case 'l':
        // Next page
        const { next } = findNavLinks();
        if (next) {
          next.click();
          e.preventDefault();
        }
        break;

      case '/':
        // Focus search
        if (focusSearch()) {
          e.preventDefault();
        }
        break;

      case 'Escape':
        // Blur active element
        if (document.activeElement) {
          document.activeElement.blur();
          e.preventDefault();
        }
        break;
    }
  }

  /**
   * Add visual indicator for vim mode
   */
  function addStatusIndicator() {
    const style = document.createElement('style');
    style.textContent = `
      .vim-nav-indicator {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.75);
        color: #fff;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        z-index: 9999;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
      }
      .vim-nav-indicator.show {
        opacity: 1;
      }
    `;
    document.head.appendChild(style);

    const indicator = document.createElement('div');
    indicator.className = 'vim-nav-indicator';
    indicator.textContent = 'Vim navigation active';
    document.body.appendChild(indicator);

    // Show indicator briefly on page load
    setTimeout(() => {
      indicator.classList.add('show');
      setTimeout(() => {
        indicator.classList.remove('show');
      }, 2000);
    }, 500);
  }

  /**
   * Initialize
   */
  function init() {
    // Attach keyboard listener
    document.addEventListener('keydown', handleKeyPress);

    // Add visual indicator
    addStatusIndicator();

    // Log initialization
    console.log('[Vim Navigation] Initialized. Keybindings: j/k (scroll), d/u (half-page), gg/G (top/bottom), h/l (prev/next), / (search)');
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
