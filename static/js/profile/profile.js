const bioField = document.querySelector('textarea[name="bio"]');

if (bioField) {
  bioField.addEventListener('input', (event) => {
    if (event.target) {
      event.target.dataset.dirty = 'true';
    }
  });
}
