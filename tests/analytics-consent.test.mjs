import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';

const source = await readFile(new URL('../assets/site.js', import.meta.url), 'utf8');

class FakeElement {
  constructor(tagName, elements) {
    this.tagName = tagName;
    this.children = [];
    this.dataset = {};
    this.hidden = false;
    this.listeners = {};
    elements.push(this);
  }

  addEventListener(type, listener) {
    this.listeners[type] = listener;
  }

  append(...children) {
    this.children.push(...children);
  }

  focus() {}

  querySelector() {
    return null;
  }

  setAttribute(name, value) {
    this[name] = value;
  }

  toggleAttribute(name, value) {
    this[name] = value;
  }
}

const runPage = ({ consent, search = '', hash = '' } = {}) => {
  const elements = [];
  const appendedScripts = [];
  const cookieWrites = [];
  const storage = new Map();
  if (consent) storage.set('cc_analytics_consent_v1', consent);

  const document = {
    body: { append() {} },
    documentElement: { lang: 'tr' },
    head: {
      append(element) {
        if (element.tagName === 'script') appendedScripts.push(element);
      },
    },
    title: 'Test sayfası',
    createElement(tagName) {
      return new FakeElement(tagName, elements);
    },
    getElementById(id) {
      return elements.find((element) => element.id === id) || null;
    },
    querySelectorAll() {
      return [];
    },
  };
  Object.defineProperty(document, 'cookie', {
    get: () => '_ga=test; _ga_TEST=test',
    set: (value) => cookieWrites.push(value),
  });

  const window = {
    localStorage: {
      getItem: (key) => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
    },
    location: {
      hash,
      hostname: 'cagricakir.com.tr',
      origin: 'https://cagricakir.com.tr',
      pathname: '/index.html',
      search,
    },
    matchMedia: () => ({ addEventListener() {}, matches: false }),
  };

  vm.runInNewContext(source, { Date, document, encodeURIComponent, window });
  return {
    appendedScripts,
    get calls() {
      return (window.dataLayer || []).map((args) => Array.from(args));
    },
    cookieWrites,
    elements,
    storage,
    window,
  };
};

const finishGoogleLoad = (result) => {
  assert.equal(result.appendedScripts.length, 1);
  result.appendedScripts[0].listeners.load();
};

test('does not load Google before explicit acceptance', () => {
  const result = runPage();

  assert.equal(result.appendedScripts.length, 0);
  assert.equal(result.window['ga-disable-G-W92EZDY9L4'], true);
  assert.deepEqual(result.calls[0].slice(0, 2), ['consent', 'default']);
  assert.equal(result.calls[0][2].analytics_storage, 'denied');
  assert.equal(result.calls[0][2].ad_storage, 'denied');
});

test('sends one sanitised page_view with advertising signals disabled', () => {
  const result = runPage({ consent: 'granted' });
  const config = result.calls.find((call) => call[0] === 'config');

  assert.equal(result.appendedScripts.length, 1);
  assert.equal(result.appendedScripts[0].src, 'https://www.googletagmanager.com/gtag/js?id=G-W92EZDY9L4');
  assert.equal(result.window['ga-disable-G-W92EZDY9L4'], false);
  assert.equal(config[2].send_page_view, false);
  assert.equal(config[2].allow_google_signals, false);
  assert.equal(config[2].allow_ad_personalization_signals, false);
  assert.equal(result.calls.some((call) => call[0] === 'event' && call[1] === 'page_view'), false);

  finishGoogleLoad(result);
  const pageView = result.calls.find((call) => call[0] === 'event' && call[1] === 'page_view');
  assert.deepEqual(JSON.parse(JSON.stringify(pageView[2])), {
    page_location: 'https://cagricakir.com.tr/index.html',
    page_path: '/index.html',
    page_title: 'Test sayfası',
    page_referrer: '',
  });
});

test('excludes URLs carrying query or hash data', () => {
  for (const location of [{ search: '?email=test@example.com' }, { hash: '#private-fragment' }]) {
    const result = runPage({ consent: 'granted', ...location });
    assert.equal(result.appendedScripts.length, 0);
    assert.equal(result.calls.length, 0);
  }
});

test('withdrawal denies consent and clears accessible analytics cookies', () => {
  const result = runPage({ consent: 'granted' });
  const manage = result.elements.find((element) => element.textContent === 'Çerez tercihleri');
  const reject = result.elements.find((element) => element.textContent === 'Reddet');

  finishGoogleLoad(result);
  manage.listeners.click();
  reject.listeners.click();

  assert.equal(result.storage.get('cc_analytics_consent_v1'), 'denied');
  assert.equal(result.window['ga-disable-G-W92EZDY9L4'], true);
  assert.ok(result.cookieWrites.some((value) => value.startsWith('_ga=') && value.includes('Max-Age=0')));
  assert.ok(result.cookieWrites.some((value) => value.startsWith('_ga_TEST=') && value.includes('Max-Age=0')));
  const lastConsentUpdate = result.calls.filter((call) => call[0] === 'consent' && call[1] === 'update').at(-1);
  assert.equal(lastConsentUpdate[2].analytics_storage, 'denied');
  assert.equal(lastConsentUpdate[2].ad_storage, 'denied');
  assert.equal(result.calls.filter((call) => call[0] === 'event' && call[1] === 'page_view').length, 1);
});

test('withdrawal while Google is loading cancels the queued page view and delayed collection', () => {
  const result = runPage({ consent: 'granted' });
  const manage = result.elements.find((element) => element.textContent === 'Çerez tercihleri');
  const reject = result.elements.find((element) => element.textContent === 'Reddet');

  manage.listeners.click();
  reject.listeners.click();
  assert.equal(result.window['ga-disable-G-W92EZDY9L4'], true);

  finishGoogleLoad(result);
  assert.equal(result.calls.filter((call) => call[0] === 'event' && call[1] === 'page_view').length, 0);
  const delayedCollections = result.window['ga-disable-G-W92EZDY9L4'] ? 0 : 1;
  assert.equal(delayedCollections, 0);
});

test('renewed acceptance re-enables collection and sends one fresh page view', () => {
  const result = runPage({ consent: 'granted' });
  const manage = result.elements.find((element) => element.textContent === 'Çerez tercihleri');
  const reject = result.elements.find((element) => element.textContent === 'Reddet');
  const accept = result.elements.find((element) => element.textContent === 'Analizi kabul et');

  finishGoogleLoad(result);
  manage.listeners.click();
  reject.listeners.click();
  manage.listeners.click();
  accept.listeners.click();

  assert.equal(result.window['ga-disable-G-W92EZDY9L4'], false);
  assert.equal(result.appendedScripts.length, 1);
  assert.equal(result.calls.filter((call) => call[0] === 'event' && call[1] === 'page_view').length, 2);
});

test('reject and re-accept during loading emits only the latest accepted page view', () => {
  const result = runPage({ consent: 'granted' });
  const manage = result.elements.find((element) => element.textContent === 'Çerez tercihleri');
  const reject = result.elements.find((element) => element.textContent === 'Reddet');
  const accept = result.elements.find((element) => element.textContent === 'Analizi kabul et');

  manage.listeners.click();
  reject.listeners.click();
  manage.listeners.click();
  accept.listeners.click();
  finishGoogleLoad(result);

  assert.equal(result.window['ga-disable-G-W92EZDY9L4'], false);
  assert.equal(result.calls.filter((call) => call[0] === 'event' && call[1] === 'page_view').length, 1);
});
