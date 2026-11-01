(() => {
  const menus = document.querySelectorAll('.nav-menu');
  const mobile = window.matchMedia('(max-width: 900px)');

  const syncMenus = () => {
    menus.forEach((menu) => menu.toggleAttribute('open', !mobile.matches));
  };

  syncMenus();
  mobile.addEventListener('change', syncMenus);
})();
