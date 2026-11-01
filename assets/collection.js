(() => {
  const filters = [...document.querySelectorAll('.collection-filter')];
  const cards = [...document.querySelectorAll('.collection-card')];

  if (!filters.length || !cards.length) return;

  const applyFilter = (filter) => {
    filters.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.filter === filter));
    });

    cards.forEach((card) => {
      card.hidden = filter !== 'all' && card.dataset.category !== filter;
    });
  };

  filters.forEach((button) => {
    button.addEventListener('click', () => applyFilter(button.dataset.filter));
  });
})();
