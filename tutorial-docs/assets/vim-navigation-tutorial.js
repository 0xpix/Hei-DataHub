/**
 * Vim-like Keyboard Navigation for Tutorial Docs
 *
 * Keybindings:
 *   j/k        - Scroll down/up (smooth)
 *   d/u        - Scroll down/up by half page
 *   gg         - Jump to top of page
 *   G          - Jump to bottom of page
 *   h/l        - Navigate to previous/next page
 *   /          - Focus search box
 *   :user      - Return to user documentation
 *   :dev       - Go to developer documentation
 *   Escape     - Exit input focus
 */

(function() {
  'use strict';

  // Configuration
  const config = {
    scrollStep: 60,
    scrollSmooth: true,
    enableInInputs: false,
    userDocsUrl: 'https://0xpix.github.io/Hei-DataHub/',
    devDocsUrl: 'https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1',
  };

  // State
  let ggBuffer = false;
  let ggTimeout = null;
  let commandMode = false;
  let commandInput = null;

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
   */
  function findNavLinks() {
    const selectors = {
      prev: [
        'a[rel="prev"]',
        '.md-footer__link--prev',
        'a.prev-page',
        'nav .previous a',
      ],
      next: [
        'a[rel="next"]',
        '.md-footer__link--next',
        'a.next-page',
        'nav .next a',
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
      '.md-search__input',
      '#mkdocs-search-query',
    ];

    for (const selector of searchSelectors) {
      const input = document.querySelector(selector);
      if (input) {
        input.focus();
        return true;
      }
    }
    return false;
  }

  /**
   * Create command input bar (vim-like command mode)
   */
  function createCommandInput() {
    const container = document.createElement('div');
    container.id = 'vim-command-container';
    container.style.cssText = `
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: #282a36;
      border-top: 2px solid #44475a;
      padding: 8px 16px;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 14px;
      z-index: 9999;
      box-shadow: 0 -2px 8px rgba(0,0,0,0.3);
      display: none;
    `;

    const prompt = document.createElement('span');
    prompt.textContent = ':';
    prompt.style.cssText = `
      color: #8be9fd;
      margin-right: 4px;
      font-weight: bold;
    `;

    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'vim-command-input';
    input.placeholder = 'Type "user" or "dev" to switch docs';
    input.style.cssText = `
      border: none;
      background: transparent;
      outline: none;
      font-family: inherit;
      font-size: inherit;
      color: #f8f8f2;
      width: calc(100% - 20px);
    `;

    container.appendChild(prompt);
    container.appendChild(input);
    document.body.appendChild(container);

    // Handle command execution
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        executeCommand(input.value.trim());
        exitCommandMode();
      } else if (e.key === 'Escape') {
        exitCommandMode();
      }
    });

    // Close on outside click
    input.addEventListener('blur', () => {
      setTimeout(exitCommandMode, 100);
    });

    return { container, input };
  }

  /**
   * Enter command mode
   */
  function enterCommandMode() {
    if (commandMode) return;

    if (!commandInput) {
      const created = createCommandInput();
      commandInput = created.input;
      commandInput.container = created.container;
    }

    commandMode = true;
    commandInput.container.style.display = 'block';
    commandInput.value = '';
    commandInput.focus();
  }

  /**
   * Exit command mode
   */
  function exitCommandMode() {
    if (!commandMode) return;
    commandMode = false;
    if (commandInput && commandInput.container) {
      commandInput.container.style.display = 'none';
      commandInput.value = '';
    }
  }

  /**
   * Execute vim command
   */
  function executeCommand(cmd) {
    console.log('Executing command:', cmd);

    switch(cmd.toLowerCase()) {
      case 'user':
      case 'u':
        // Navigate to user docs
        console.log('Navigating to user docs:', config.userDocsUrl);
        window.location.href = config.userDocsUrl;
        break;

      case 'dev':
      case 'd':
        // Navigate to dev docs
        console.log('Navigating to dev docs:', config.devDocsUrl);
        window.location.href = config.devDocsUrl;
        break;

      case 'q':
      case 'quit':
        // Close tab (may not work in all browsers)
        window.close();
        break;

      default:
        console.log('Unknown command:', cmd);
        // Show error briefly
        if (commandInput) {
          commandInput.value = 'Unknown command: ' + cmd;
          setTimeout(() => {
            exitCommandMode();
          }, 1000);
        }
    }
  }

  /**
   * Main keyboard event handler
   */
  function handleKeyPress(e) {
    // Allow normal behavior in input fields (unless explicitly enabled)
    if (!config.enableInInputs && isTyping() && !commandMode) {
      return;
    }

    // In command mode, only handle Escape
    if (commandMode) {
      if (e.key === 'Escape') {
        e.preventDefault();
        exitCommandMode();
      }
      return;
    }

    const key = e.key.toLowerCase();

    // Command mode trigger
    if (key === ':' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      enterCommandMode();
      return;
    }

    // Vertical scrolling
    if (key === 'j' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      scrollBy(config.scrollStep);
      return;
    }

    if (key === 'k' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      scrollBy(-config.scrollStep);
      return;
    }

    // Half-page scrolling
    if (key === 'd' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      scrollBy(window.innerHeight / 2);
      return;
    }

    if (key === 'u' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      scrollBy(-window.innerHeight / 2);
      return;
    }

    // Jump to top/bottom
    if (key === 'g') {
      if (ggBuffer) {
        // Second 'g' - jump to top
        e.preventDefault();
        scrollTo(0);
        ggBuffer = false;
        if (ggTimeout) clearTimeout(ggTimeout);
      } else {
        // First 'g' - start buffer
        ggBuffer = true;
        ggTimeout = setTimeout(() => {
          ggBuffer = false;
        }, 500);
      }
      return;
    }

    if (key === 'G' && e.shiftKey) {
      e.preventDefault();
      scrollTo(document.body.scrollHeight);
      return;
    }

    // Page navigation
    if (key === 'h' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      const { prev } = findNavLinks();
      if (prev) prev.click();
      return;
    }

    if (key === 'l' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      const { next } = findNavLinks();
      if (next) next.click();
      return;
    }

    // Search
    if (key === '/' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      focusSearch();
      return;
    }

    // Escape - blur active element
    if (key === 'Escape') {
      document.activeElement?.blur();
      return;
    }
  }

  // Initialize
  document.addEventListener('keydown', handleKeyPress);

  console.log('[Tutorial Vim Navigation] Initialized with commands: :user, :dev');
})();
