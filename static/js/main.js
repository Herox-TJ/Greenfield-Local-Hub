document.addEventListener('DOMContentLoaded', function () {

    //quantity +/- buttons
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

    //cart quantity inline update on change
    document.querySelectorAll('.cart-qty-input').forEach(function (input) {
        input.addEventListener('change', function () {
            input.closest('form').submit();
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
});