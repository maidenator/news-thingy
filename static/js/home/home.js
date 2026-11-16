document.querySelectorAll('.source-row form').forEach((form) => form.addEventListener('submit', () => form.querySelector('button').disabled = true));
