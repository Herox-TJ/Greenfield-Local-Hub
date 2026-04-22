// dark mode
const themeToggle = document.getElementById('theme-toggle');
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
if (themeToggle) {
    themeToggle.textContent = savedTheme === 'dark' ? '☀' : '☾';
    themeToggle.addEventListener('click', function() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        themeToggle.textContent = next === 'dark' ? '☀' : '☾';
    });
}

//cookie banner
(function () {
    var consent = localStorage.getItem('glh_cookie_consent');
    if (!consent) {
        var overlay = document.getElementById('cookie-overlay');
        if (overlay) overlay.style.display = 'flex';
    }

    function closeBanner() {
        var overlay = document.getElementById('cookie-overlay');
        if (overlay) overlay.style.display = 'none';
    }
    function closePrefs() {
        var panel = document.getElementById('cookie-prefs-panel');
        if (panel) panel.style.display = 'none';
    }

    var btnAccept = document.getElementById('cookie-accept');
    if (btnAccept) btnAccept.addEventListener('click', function () {
        localStorage.setItem('glh_cookie_consent', 'accepted');
        closeBanner();
    });

    var btnClose = document.getElementById('cookie-close');
    if (btnClose) btnClose.addEventListener('click', function () {
        localStorage.setItem('glh_cookie_consent', 'dismissed');
        closeBanner();
    });

    var btnPrefs = document.getElementById('cookie-prefs');
    if (btnPrefs) btnPrefs.addEventListener('click', function () {
        closeBanner();
        var panel = document.getElementById('cookie-prefs-panel');
        if (panel) panel.style.display = 'flex';
    });

    var btnPrefsClose = document.getElementById('cookie-prefs-close');
    if (btnPrefsClose) btnPrefsClose.addEventListener('click', closePrefs);

    var btnSavePrefs = document.getElementById('cookie-save-prefs');
    if (btnSavePrefs) btnSavePrefs.addEventListener('click', function () {
        var analytics = document.getElementById('pref-analytics');
        var marketing = document.getElementById('pref-marketing');
        localStorage.setItem('glh_cookie_consent', 'custom');
        localStorage.setItem('glh_cookie_analytics', analytics && analytics.checked ? '1' : '0');
        localStorage.setItem('glh_cookie_marketing', marketing && marketing.checked ? '1' : '0');
        closePrefs();
    });

    // close overlay when clicking outside the modal
    var overlay = document.getElementById('cookie-overlay');
    if (overlay) overlay.addEventListener('click', function (e) {
        if (e.target === overlay) {
            localStorage.setItem('glh_cookie_consent', 'dismissed');
            closeBanner();
        }
    });
    var prefsPanel = document.getElementById('cookie-prefs-panel');
    if (prefsPanel) prefsPanel.addEventListener('click', function (e) {
        if (e.target === prefsPanel) closePrefs();
    });
}());

document.addEventListener('DOMContentLoaded', function () {

    //quantity +/- buttons (product detail page)
    document.querySelectorAll('.qty-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var input = btn.closest('.qty-ctrl').querySelector('.qty-input');
            var val = parseInt(input.value) || 1;
            if (btn.dataset.action === 'inc') {
                input.value = val + 1;
            } else if (btn.dataset.action === 'dec' && val > 1) {
                input.value = val - 1;
            }
        });
    });

    //cart quantity +/- buttons (cart page)
    document.querySelectorAll('.cart-qty-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var itemId = btn.dataset.itemId;
            var numEl = document.querySelector('.cart-qty-num[data-item-id="' + itemId + '"]');
            if (!numEl) return;
            var val = parseInt(numEl.value) || 1;
            if (btn.dataset.action === 'inc') {
                numEl.value = val + 1;
            } else if (btn.dataset.action === 'dec' && val > 1) {
                numEl.value = val - 1;
            }
            // submit the hidden form
            var form = document.querySelector('.cart-update-form[data-item-id="' + itemId + '"]');
            if (form) {
                form.querySelector('input[name="quantity"]').value = numEl.value;
                form.submit();
            }
        });
    });

    //auto-dismiss flash messages after 4 s
    setTimeout(function () {
        document.querySelectorAll('.flash').forEach(function (el) {
            el.style.transition = 'opacity .5s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 500);
        });
    }, 4000);

    //checkout fulfillment card selection
    var addressSection = document.querySelector('.checkout-address');

    function updateAddressVisibility() {
        var selected = document.querySelector('input[name="fulfillment"]:checked');
        if (!addressSection) return;
        var ta = addressSection.querySelector('textarea');
        if (selected && selected.value === 'collection') {
            addressSection.style.display = 'none';
            if (ta) ta.removeAttribute('required');
        } else {
            addressSection.style.display = '';
            if (ta) ta.setAttribute('required', '');
        }
    }

    document.querySelectorAll('.fulfillment-card').forEach(function (card) {
        card.addEventListener('click', function () {
            document.querySelectorAll('.fulfillment-card').forEach(function (c) {
                c.classList.remove('selected');
            });
            card.classList.add('selected');
            var radio = card.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
            updateAddressVisibility();
        });
    });

    updateAddressVisibility();

}); 