document.addEventListener('DOMContentLoaded', () => {
  const icon = document.querySelector('.md-source.source-detail .md-source-repo-icon');
  if (!icon) return;

  const url = 'https://github.com/0xpix/Hei-DataHub';

  const go = () => window.open(url, '_blank', 'noopener,noreferrer');

  icon.style.cursor = 'pointer';
  icon.setAttribute('role', 'link');
  icon.setAttribute('tabindex', '0');
  icon.title = 'Open repository';

  icon.addEventListener('click', go);
  icon.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); }
  });
});
