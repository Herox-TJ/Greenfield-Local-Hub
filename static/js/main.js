document.addEventListener('DOMContentLoaded', function () {

    // ── auto-dismiss flash messages after 4 s ────────────────────────────────
    setTimeout(function () {
        document.querySelectorAll('.flash').forEach(function (el) {
            el.style.transition = 'opacity .5s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 500);
        });
    }, 4000);

});
 