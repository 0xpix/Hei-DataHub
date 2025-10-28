/**
 * Automatically set correct repository URL for edit links
 * This script updates edit links to use the correct branch based on the docs type
 */

(function() {
  'use strict';

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    // Detect if we're in tutorial docs by checking URL
    const isTutorialDocs = window.location.pathname.includes('/tutorial/');

    if (isTutorialDocs) {
      // Update edit links to point to tutorial-docs branch
      updateEditLinks('tutorial-docs');
    }
  }

  function updateEditLinks(branch) {
    const editLinks = document.querySelectorAll('a[href*="/edit/"]');

    editLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href) {
        // Replace the branch in the edit URL
        const newHref = href.replace(/\/edit\/[^/]+\//, `/edit/${branch}/`);
        link.setAttribute('href', newHref);
        console.log(`[Repo URL] Updated edit link to use branch: ${branch}`);
      }
    });
  }
})();
