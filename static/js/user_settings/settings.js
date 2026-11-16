document.querySelectorAll('.toggle input').forEach((input) => input.addEventListener('change', () => input.closest('form').dataset.changed = 'true'));
