// ===== Auto-set today's date in date inputs =====
document.addEventListener('DOMContentLoaded', function () {

    // لو فيه input نوعه date وفاضي — حط تاريخ النهارده تلقائي
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function (input) {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });

    // ===== Auto-hide flash messages بعد 4 ثواني =====
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 4000);
    });

});
