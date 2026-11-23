document.querySelectorAll('.toggle input').forEach((input) => {
  input.addEventListener('change', () => {
    const form = input.closest('form');
    if (form) {
      form.dataset.changed = 'true';
    }
  });
});
