/**
 * Vim-like Keyboard Navigation for Developer Docs
 * 
 * This is a simplified version for developer documentation.
 * 
 * Keybindings:
 *   j/k        - Scroll down/up (smooth)
 *   d/u        - Scroll down/up by half page
 *   gg         - Jump to top of page
 *   G          - Jump to bottom of page
 *   h/l        - Navigate to previous/next page
 *   /          - Focus search box
 *   :user      - Return to user documentation
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
      background: #f8f9fa;
      border-top: 2px solid #dee2e6;
      padding: 8px 16px;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 14px;
      z-index: 9999;
      box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
      display: none;
    `;

    const prompt = document.createElement('span');
    prompt.textContent = ':';
    prompt.style.cssText = `
      color: #495057;
      margin-right: 4px;
      font-weight: bold;
    `;

    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'vim-command-input';
    input.style.cssText = `
      border: none;
      background: transparent;
      outline: none;
      font-family: inherit;
      font-size: inherit;
      color: #212529;
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

    // Handle command mode separately
    if (commandMode) {
      return; // Let command input handle its own keys
    }

    const key = e.key;

    // Escape - blur active element
    if (key === 'Escape') {
      if (document.activeElement) {
        document.activeElement.blur();
      }
      return;
    }

    // Prevent default for vim keys (but not in inputs)
    const shouldPreventDefault = !isTyping() && (
      ['j', 'k', 'd', 'u', 'g', 'G', 'h', 'l', '/', ':'].includes(key)
    );

    if (shouldPreventDefault) {
      e.preventDefault();
    }

    // Command mode trigger
    if (key === ':' && !isTyping()) {
      enterCommandMode();
      return;
    }

    // Search trigger
    if (key === '/' && !isTyping()) {
      focusSearch();
      return;
    }

    // Navigation
    const { prev, next } = findNavLinks();

    switch (key) {
      case 'j':
        scrollBy(config.scrollStep);
        break;

      case 'k':
        scrollBy(-config.scrollStep);
        break;

      case 'd':
        scrollBy(window.innerHeight / 2);
        break;

      case 'u':
        scrollBy(-window.innerHeight / 2);
        break;

      case 'g':
        if (ggBuffer) {
          // Second 'g' - go to top
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
        break;

      case 'G':
        scrollTo(document.body.scrollHeight);
        break;

      case 'h':
        if (prev) {
          prev.click();
        }
        break;

      case 'l':
        if (next) {
          next.click();
        }
        break;
    }
  }

  /**
   * Show vim keybinding hint on first visit
   */
  function showKeybindingHint() {
    // Check if user has seen the hint
    if (localStorage.getItem('vim-hint-seen-dev')) {
      return;
    }

    const hint = document.createElement('div');
    hint.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      font-size: 14px;
      z-index: 9998;
      max-width: 300px;
      animation: slideIn 0.3s ease-out;
    `;

    hint.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 8px;">💡 Vim Navigation Active</div>
      <div style="font-size: 12px; opacity: 0.95; line-height: 1.5;">
        Use <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">j/k</code> to scroll,
        <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">gg/G</code> for top/bottom,
        <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">/</code> for search<br>
        Type <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">:user</code> to return to user docs
      </div>
      <button id="vim-hint-close" style="
        margin-top: 10px;
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
      ">Got it!</button>
    `;

    document.body.appendChild(hint);

    // Close handler
    document.getElementById('vim-hint-close').addEventListener('click', () => {
      hint.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => hint.remove(), 300);
      localStorage.setItem('vim-hint-seen-dev', 'true');
    });

    // Auto-hide after 10 seconds
    setTimeout(() => {
      if (hint.parentNode) {
        hint.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => hint.remove(), 300);
        localStorage.setItem('vim-hint-seen-dev', 'true');
      }
    }, 10000);
  }

  /**
   * Add CSS animations
   */
  function addStyles() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(400px);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      
      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(400px);
          opacity: 0;
        }
      }

      /* Dark mode support for command bar */
      @media (prefers-color-scheme: dark) {
        #vim-command-container {
          background: #2d3748 !important;
          border-top-color: #4a5568 !important;
        }
        #vim-command-container span {
          color: #e2e8f0 !important;
        }
        #vim-command-input {
          color: #f7fafc !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Initialize
   */
  function init() {
    // Add event listener
    document.addEventListener('keydown', handleKeyPress);

    // Add styles
    addStyles();

    // Show hint on first visit
    setTimeout(showKeybindingHint, 1000);

    console.log('Vim navigation loaded (Developer Docs)');
    console.log('Keybindings: j/k (scroll), gg/G (top/bottom), h/l (prev/next), / (search), :user (return to user docs)');
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
