(() => {
  const menus = document.querySelectorAll('.nav-menu');
  const mobile = window.matchMedia('(max-width: 900px)');

  const syncMenus = () => {
    menus.forEach((menu) => menu.toggleAttribute('open', !mobile.matches));
  };

  syncMenus();
  mobile.addEventListener('change', syncMenus);

  const MEASUREMENT_ID = 'G-W92EZDY9L4';
  const CONSENT_KEY = 'cc_analytics_consent_v1';
  const COOKIE_DOMAIN = '.cagricakir.com.tr';
  const pagePath = window.location.pathname;
  if (window.location.search !== '' || window.location.hash !== '') return;
  const DISABLE_KEY = `ga-disable-${MEASUREMENT_ID}`;
  window[DISABLE_KEY] = true;

  const isEnglish = document.documentElement.lang.toLowerCase().startsWith('en');
  const copy = isEnglish
    ? {
        title: 'Your analytics choice',
        body: 'With your permission, Google Analytics helps measure visits and improve this site. It is not loaded before you accept.',
        accept: 'Accept analytics',
        reject: 'Reject',
        manage: 'Cookie preferences',
        privacy: 'Privacy notice',
        privacyHref: 'privacy.html',
      }
    : {
        title: 'Analiz tercihiniz',
        body: 'İzninizle Google Analytics ziyaretleri ölçmeye ve siteyi geliştirmeye yardımcı olur. Kabul etmeden önce yüklenmez.',
        accept: 'Analizi kabul et',
        reject: 'Reddet',
        manage: 'Çerez tercihleri',
        privacy: 'Gizlilik bildirimi',
        privacyHref: 'gizlilik.html',
      };

  window.dataLayer = window.dataLayer || [];
  const gtag =
    typeof window.gtag === 'function'
      ? window.gtag
      : function gtag() {
          window.dataLayer.push(arguments);
        };
  window.gtag = gtag;

  const deniedConsent = {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
  };

  gtag('consent', 'default', {
    ...deniedConsent,
    functionality_storage: 'granted',
    security_storage: 'granted',
    wait_for_update: 500,
  });
  gtag('set', 'ads_data_redaction', true);
  gtag('set', 'allow_google_signals', false);

  let analyticsLoaded = false;
  let analyticsScriptReady = false;
  let analyticsEnabled = false;
  let pendingPageView = false;

  const readConsent = () => {
    try {
      const value = window.localStorage.getItem(CONSENT_KEY);
      return value === 'granted' || value === 'denied' ? value : null;
    } catch (_error) {
      return null;
    }
  };

  const saveConsent = (value) => {
    try {
      window.localStorage.setItem(CONSENT_KEY, value);
    } catch (_error) {
      // Restricted browsers may disable storage. The current-page choice still
      // applies, and the visitor is asked again on a later visit.
    }
  };

  const clearAnalyticsCookies = () => {
    const host = window.location.hostname;
    document.cookie.split(';').forEach((item) => {
      const name = item.split('=')[0].trim();
      if (!name.startsWith('_ga')) return;
      document.cookie = `${name}=; Max-Age=0; path=/; SameSite=Lax`;
      document.cookie = `${name}=; Max-Age=0; path=/; domain=${host}; SameSite=Lax`;
      document.cookie = `${name}=; Max-Age=0; path=/; domain=${COOKIE_DOMAIN}; SameSite=Lax`;
    });
  };

  const sendPageView = () => {
    if (!analyticsEnabled || !analyticsScriptReady || !pendingPageView) return;
    pendingPageView = false;
    const pageLocation = `${window.location.origin}${pagePath}`;
    gtag('event', 'page_view', {
      page_location: pageLocation,
      page_path: pagePath,
      page_title: document.title,
      page_referrer: '',
    });
  };

  const loadAnalytics = () => {
    const wasEnabled = analyticsEnabled;
    window[DISABLE_KEY] = false;
    analyticsEnabled = true;
    gtag('consent', 'update', { analytics_storage: 'granted' });
    if (!wasEnabled) pendingPageView = true;
    if (analyticsLoaded || document.getElementById('google-analytics-tag')) {
      sendPageView();
      return;
    }
    analyticsLoaded = true;

    gtag('js', new Date());
    gtag('config', MEASUREMENT_ID, {
      send_page_view: false,
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      cookie_flags: 'SameSite=Lax;Secure',
    });
    const script = document.createElement('script');
    script.id = 'google-analytics-tag';
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(MEASUREMENT_ID)}`;
    script.addEventListener('load', () => {
      analyticsScriptReady = true;
      sendPageView();
    });
    document.head.append(script);
  };

  const disableAnalytics = () => {
    window[DISABLE_KEY] = true;
    analyticsEnabled = false;
    pendingPageView = false;
    gtag('consent', 'update', deniedConsent);
    clearAnalyticsCookies();
  };

  const banner = document.createElement('section');
  banner.className = 'consent-banner';
  banner.hidden = true;
  banner.setAttribute('role', 'dialog');
  banner.tabIndex = -1;
  banner.setAttribute('aria-labelledby', 'consent-title');
  banner.setAttribute('aria-describedby', 'consent-description');

  const content = document.createElement('div');
  content.className = 'consent-banner__content';

  const text = document.createElement('div');
  text.className = 'consent-banner__text';
  const title = document.createElement('strong');
  title.id = 'consent-title';
  title.textContent = copy.title;
  const description = document.createElement('p');
  description.id = 'consent-description';
  description.textContent = copy.body;
  const privacy = document.createElement('a');
  privacy.href = copy.privacyHref;
  privacy.textContent = copy.privacy;
  text.append(title, description, privacy);

  const actions = document.createElement('div');
  actions.className = 'consent-banner__actions';
  const reject = document.createElement('button');
  reject.type = 'button';
  reject.className = 'consent-button consent-button--secondary';
  reject.textContent = copy.reject;
  const accept = document.createElement('button');
  accept.type = 'button';
  accept.className = 'consent-button consent-button--primary';
  accept.textContent = copy.accept;
  actions.append(reject, accept);
  content.append(text, actions);
  banner.append(content);

  const manage = document.createElement('button');
  manage.type = 'button';
  manage.className = 'consent-manage';
  manage.textContent = copy.manage;
  manage.hidden = true;

  const showBanner = () => {
    banner.hidden = false;
    manage.hidden = true;
    banner.focus();
  };

  const hideBanner = () => {
    banner.hidden = true;
    manage.hidden = false;
  };

  const setConsent = (value) => {
    saveConsent(value);
    if (value === 'granted') {
      loadAnalytics();
    } else {
      disableAnalytics();
    }
    hideBanner();
  };

  accept.addEventListener('click', () => setConsent('granted'));
  reject.addEventListener('click', () => setConsent('denied'));
  manage.addEventListener('click', showBanner);
  banner.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && readConsent()) hideBanner();
  });

  document.querySelectorAll('.footer-links').forEach((links) => {
    if (links.querySelector('[data-privacy-link]')) return;
    const link = document.createElement('a');
    link.href = copy.privacyHref;
    link.textContent = copy.privacy;
    link.dataset.privacyLink = 'true';
    links.append(link);
  });

  document.body.append(banner, manage);

  const storedConsent = readConsent();
  if (storedConsent === 'granted') {
    loadAnalytics();
    manage.hidden = false;
  } else if (storedConsent === 'denied') {
    manage.hidden = false;
  } else {
    showBanner();
  }
})();
