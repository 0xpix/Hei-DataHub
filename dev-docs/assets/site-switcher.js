/**
 * Site Switcher JavaScript
 * Adds functionality to toggle between User Docs and Developer Docs sites
 */

(function() {
    'use strict';

    // Configuration
    const SITES = {
        user: {
            name: 'User Manual',
            url: 'https://0xpix.github.io/Hei-DataHub',
            icon: '📖',
            description: 'For end users and data analysts'
        },
        dev: {
            name: 'Developer Docs',
            url: 'https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1',
            icon: '🔧',
            description: 'For contributors and maintainers'
        }
    };

    // Detect current site
    const currentSite = window.location.pathname.includes('/x9k2m7n4p8q1') ? 'x9k2m7n4p8q1' : 'user';
    const otherSite = currentSite === 'x9k2m7n4p8q1' ? 'user' : 'x9k2m7n4p8q1';

    /**
     * Create site switcher banner
     */
    function createSiteSwitcher() {
        const banner = document.createElement('div');
        banner.className = 'site-switcher-banner';
        banner.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            text-align: center;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            font-size: 0.9rem;
        `;

        banner.innerHTML = `
            <span style="font-weight: 600;">
                ${SITES[currentSite].icon} You are viewing: <strong>${SITES[currentSite].name}</strong>
            </span>
            <span style="margin: 0 1rem;">|</span>
            <a href="${SITES[otherSite].url}"
               style="color: #fbbf24; text-decoration: underline; font-weight: 600;">
                ${SITES[otherSite].icon} Switch to ${SITES[otherSite].name}
            </a>
        `;

        document.body.insertBefore(banner, document.body.firstChild);

        // Add top padding to prevent content overlap
        const header = document.querySelector('.md-header');
        if (header) {
            header.style.marginTop = '40px';
        }
    }

    /**
     * Add site indicator to navigation
     */
    function addSiteIndicator() {
        const nav = document.querySelector('.md-nav--primary');
        if (!nav) return;

        const indicator = document.createElement('div');
        indicator.className = 'site-indicator';
        indicator.style.cssText = `
            padding: 1rem;
            margin: 0.5rem;
            background: ${currentSite === 'x9k2m7n4p8q1' ? '#6366f1' : '#059669'};
            color: white;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            font-size: 0.85rem;
        `;

        indicator.innerHTML = `
            ${SITES[currentSite].icon}<br>
            ${SITES[currentSite].name}<br>
            <small style="opacity: 0.8;">${SITES[currentSite].description}</small>
        `;

        nav.insertBefore(indicator, nav.firstChild);
    }

    /**
     * Initialize site switcher
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        createSiteSwitcher();
        addSiteIndicator();

        // Log for debugging
        console.log(`[SiteSwitcher] Current site: ${currentSite}`);
    }

    // Run initialization
    init();

})();
