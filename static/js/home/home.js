document.querySelectorAll('.source-row form').forEach((form) => {
  form.addEventListener('submit', () => {
    const button = form.querySelector('button');
    if (button) {
      button.disabled = true;
    }
  });
});

document.querySelectorAll('.fetch-form').forEach((form) => {
  form.addEventListener('submit', () => {
    const button = form.querySelector('button');
    if (button) {
      button.disabled = true;
      button.textContent = 'Fetching…';
    }
  });
});
