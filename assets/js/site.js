(() => {
  const menu = document.getElementById('mobile-menu');
  if (!menu) return;
  const summary = menu.querySelector('summary');
  const update = () => summary.setAttribute('aria-expanded', String(menu.open));
  update();
  menu.addEventListener('toggle', update);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      summary.focus();
    }
  });
  document.addEventListener('click', event => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => { menu.open = false; }));
  const wide = window.matchMedia('(min-width: 768px)');
  wide.addEventListener('change', () => { if (wide.matches) menu.open = false; });
})();

(() => {
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); }
    }), { threshold: 0.1 });
    document.querySelectorAll('.reveal').forEach(element => observer.observe(element));
    document.documentElement.classList.add('reveal-enabled');
  }
})();
