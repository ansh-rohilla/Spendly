// main.js — students will add JavaScript here as features are built

(function () {
    'use strict';

    // -- Modal handling -----------------------------------------------

    var openButtons = document.querySelectorAll('[data-modal-open]');
    var modals = {};

    function getModal(id) {
        if (modals[id]) return modals[id];
        var el = document.getElementById(id);
        if (!el) return null;
        modals[id] = {
            el: el,
            iframe: el.querySelector('iframe[data-src]'),
            lastFocus: null
        };
        return modals[id];
    }

    function openModal(id) {
        var m = getModal(id);
        if (!m) return;
        m.lastFocus = document.activeElement;

        // Load the video only when the modal is opened — keeps the page
        // light until the user actually wants to watch.
        if (m.iframe && m.iframe.dataset.src) {
            m.iframe.src = m.iframe.dataset.src;
        }

        m.el.hidden = false;
        m.el.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');

        var closeBtn = m.el.querySelector('.modal-close');
        if (closeBtn) closeBtn.focus();
    }

    function closeModal(id) {
        var m = getModal(id);
        if (!m) return;
        m.el.hidden = true;
        m.el.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');

        // Stop the video by clearing the iframe src. The YouTube embed
        // tears down its player when the src is removed, so no audio
        // keeps playing in the background.
        if (m.iframe) {
            // Belt-and-braces: also ask the player to pause first.
            try {
                m.iframe.contentWindow.postMessage(
                    '{"event":"command","func":"pauseVideo","args":""}',
                    '*'
                );
            } catch (e) { /* iframe may be cross-origin; ignore */ }
            m.iframe.src = '';
        }

        if (m.lastFocus && typeof m.lastFocus.focus === 'function') {
            m.lastFocus.focus();
        }
    }

    openButtons.forEach(function (btn) {
        btn.addEventListener('click', function (event) {
            event.preventDefault();
            openModal(btn.dataset.modalOpen);
        });
    });

    document.addEventListener('click', function (event) {
        var closer = event.target.closest('[data-modal-close]');
        if (!closer) return;
        var modalEl = closer.closest('.modal');
        if (modalEl && modalEl.id) closeModal(modalEl.id);
    });

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var open = document.querySelector('.modal:not([hidden])');
        if (open) closeModal(open.id);
    });
})();
