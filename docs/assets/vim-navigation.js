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
 *   :          - Enter command mode (type :dev to go to developer docs)
 *   :          - Enter command mode (type :dev to go to developer docs)
 *   Escape     - Blur active element (exit input focus)
 */

(function() {
  'use strict';

  // Configuration
  const config = {
    scrollStep: 60,              // pixels for j/k
    scrollSmooth: true,          // enable smooth scrolling
    enableInInputs: false,       // allow vim keys while typing (usually false)
    // Obfuscated path to developer docs (not meant to be guessed)
    devDocsUrl: 'https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1/dev/',
  };

  // State
  let ggBuffer = false;          // track 'g' press for 'gg' command
  let ggTimeout = null;
  let commandMode = false;       // track if in command mode
  let commandInput = null;       // reference to command input element
  let commandMode = false;       // track if in command mode
  let commandInput = null;       // reference to command input element

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
   * Create command mode input overlay
   */
  function createCommandInput() {
    console.log('[Vim Navigation] Creating command input overlay');

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'vim-command-overlay';
    overlay.style.cssText = `
      position: fixed !important;
      bottom: 0 !important;
      left: 0 !important;
      right: 0 !important;
      background: #1e1e1e !important;
      color: #d4d4d4 !important;
      padding: 0.75rem 1rem !important;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
      font-size: 16px !important;
      border-top: 3px solid #007acc !important;
      z-index: 999999 !important;
      display: flex !important;
      align-items: center !important;
      box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.5) !important;
      width: 100% !important;
      box-sizing: border-box !important;
    `;

    // Create prompt
    const prompt = document.createElement('span');
    prompt.textContent = ':';
    prompt.style.cssText = `
      color: #007acc !important;
      font-weight: bold !important;
      margin-right: 0.5rem !important;
      font-size: 18px !important;
    `;

    // Create input
    const input = document.createElement('input');
    input.id = 'vim-command-input';
    input.type = 'text';
    input.autocomplete = 'off';
    input.spellcheck = false;
    input.style.cssText = `
      background: transparent !important;
      border: none !important;
      outline: none !important;
      color: #d4d4d4 !important;
      font-family: inherit !important;
      font-size: inherit !important;
      flex: 1 !important;
      padding: 0 !important;
      margin: 0 !important;
    `;
    input.placeholder = 'Type "dev" to go to Developer Docs';

    overlay.appendChild(prompt);
    overlay.appendChild(input);
    document.body.appendChild(overlay);

    console.log('[Vim Navigation] Command overlay created and appended to body');

    return { overlay, input };
  }

  /**
   * Execute vim command
   */
  function executeCommand(cmd) {
    const trimmed = cmd.trim().toLowerCase();
    console.log('[Vim Navigation] Executing command:', trimmed);

    if (trimmed === 'dev') {
      window.location.href = config.devDocsUrl;
      return true;
    }

    // Unknown command
    console.warn('[Vim Navigation] Unknown command:', trimmed);
    return false;
  }

  /**
   * Enter command mode
   */
  function enterCommandMode() {
    console.log('[Vim Navigation] enterCommandMode called, current commandMode:', commandMode);

    if (commandMode) {
      console.log('[Vim Navigation] Already in command mode, ignoring');
      return;
    }

    commandMode = true;
    console.log('[Vim Navigation] Creating command input...');

    const { overlay, input } = createCommandInput();
    commandInput = input;

    // Focus the input
    setTimeout(() => {
      input.focus();
      console.log('[Vim Navigation] Input focused');
    }, 10);

    // Handle Enter key to execute command
    input.addEventListener('keydown', (e) => {
      console.log('[Vim Navigation] Command input keydown:', e.key);

      if (e.key === 'Enter') {
        e.preventDefault();
        console.log('[Vim Navigation] Enter pressed, executing command:', input.value);
        const success = executeCommand(input.value);
        exitCommandMode();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        console.log('[Vim Navigation] Escape pressed, exiting command mode');
        exitCommandMode();
      }
    });

    console.log('[Vim Navigation] Command mode entered successfully');
  }

  /**
   * Exit command mode
   */
  function exitCommandMode() {
    if (!commandMode) return;

    commandMode = false;
    const overlay = document.getElementById('vim-command-overlay');
    if (overlay) {
      overlay.remove();
    }
    commandInput = null;

    console.log('[Vim Navigation] Exited command mode');
  }

  /**
   * Main keyboard handler
   */
  function handleKeyPress(e) {
    // Debug: log key presses (remove in production if needed)
    if (['j', 'k', 'h', 'l', 'g', 'G', 'd', 'u', '/', ':'].includes(e.key)) {
    if (['j', 'k', 'h', 'l', 'g', 'G', 'd', 'u', '/', ':'].includes(e.key)) {
      console.log('[Vim Navigation] Key pressed:', e.key, '| URL:', location.pathname);
    }

    // Handle command mode separately
    if (commandMode) {
      // Command input handles its own keys
      return;
    }

    // Handle command mode separately
    if (commandMode) {
      // Command input handles its own keys
      return;
    }

    // Allow normal behavior in input fields (unless explicitly enabled)
    if (!config.enableInInputs && isTyping()) {
      // Still allow Escape to blur
      if (e.key === 'Escape') {
        document.activeElement.blur();
        e.preventDefault();
      }
      return;
    }

    // Enter command mode with ':' (Shift + semicolon produces ':')
    if (e.key === ':') {
      e.preventDefault();
      enterCommandMode();
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
   * Initialize keyboard listener
   */
  function initKeyboardListener() {
    // Remove any existing listener first (in case of re-initialization)
    document.removeEventListener('keydown', handleKeyPress);

    // Attach keyboard listener to document
    document.addEventListener('keydown', handleKeyPress, { capture: false, passive: false });

    console.log('[Vim Navigation] Keyboard listener attached');
  }

  /**
   * Initialize
   */
  function init() {
    console.log('[Vim Navigation] Initializing on page:', location.pathname);

    // Attach keyboard listener
    initKeyboardListener();

    // Add visual indicator (only once)
    if (!document.querySelector('.vim-nav-indicator')) {
      addStatusIndicator();
    }

    // Log initialization
    console.log('[Vim Navigation] Initialized. Keybindings: j/k (scroll), d/u (half-page), gg/G (top/bottom), h/l (prev/next), / (search), : (command mode)');
    console.log('[Vim Navigation] Command mode: Type ":dev" to navigate to Developer Docs');


    // Listen for instant navigation / history changes (for MkDocs instant loading)
    // This ensures vim navigation works after client-side page transitions
    if (window.navigation) {
      // Modern Navigation API
      window.navigation.addEventListener('navigate', () => {
        console.log('[Vim Navigation] Page navigated (Navigation API)');
      });
    }

    // Listen for popstate (back/forward button)
    window.addEventListener('popstate', () => {
      console.log('[Vim Navigation] Page navigated (popstate)');
    });

    // Listen for MkDocs instant loading (Material theme)
    document.addEventListener('DOMContentSwitch', () => {
      console.log('[Vim Navigation] Page navigated (DOMContentSwitch)');
    });

    // Watch for URL changes (for instant navigation)
    let lastUrl = location.href;
    new MutationObserver(() => {
      const url = location.href;
      if (url !== lastUrl) {
        lastUrl = url;
        console.log('[Vim Navigation] Page navigated (URL change detected)');
        // Reset gg buffer on page change
        ggBuffer = false;
        clearTimeout(ggTimeout);
      }
    }).observe(document, { subtree: true, childList: true });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Also reinitialize on instant.js page loads (if present)
  document.addEventListener('DOMContentLoaded', () => {
    console.log('[Vim Navigation] DOMContentLoaded event fired');
  });

})();
