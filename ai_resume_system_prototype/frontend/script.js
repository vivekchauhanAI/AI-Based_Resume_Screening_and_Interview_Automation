const form = document.getElementById('uploadForm');
const output = document.getElementById('output');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById('resume');
  if (!fileInput.files.length) { alert('Choose a resume file first'); return; }
  const fd = new FormData();
  fd.append('resume', fileInput.files[0]);
  output.textContent = 'Uploading and analyzing...';
  try {
    const res = await fetch('/upload', { method:'POST', body: fd });
    const data = await res.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = 'Error: ' + err.toString();
  }
});
