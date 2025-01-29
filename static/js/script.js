function getVideoDetails() {
    const url = document.getElementById('video-url').value.trim();
    if (!url) {
        alert("Masukkan URL YouTube!");
        return;
    }

    fetch('/get_formats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        displayThumbnail(data.thumbnail);
        displayResolutions(data.resolutions);
    })
    .catch(error => {
        alert(`Error: ${error.message}`);
    });
}


function displayThumbnail(thumbnailUrl) {
    const thumbnailElement = document.getElementById('video-thumbnail');
    const previewContainer = document.getElementById('video-preview-container');
    
    if (thumbnailUrl) {
        thumbnailElement.src = thumbnailUrl;
        previewContainer.style.display = 'block'; // Tampilkan container
    } else {
        previewContainer.style.display = 'none'; // Sembunyikan jika tidak ada thumbnail
    }
}

function displayResolutions(resolutions) {
    const resolutionSelect = document.getElementById('resolution-select');
    resolutionSelect.innerHTML = '<option value="">Pilih Resolusi</option>';

    if (!resolutions || resolutions.length === 0) {
        alert("Video tidak memiliki resolusi 480p/720p/1080p!");
        return;
    }

    resolutions.forEach(res => {
        const option = document.createElement('option');
        option.value = res.format_id;
        option.textContent = `${res.resolution}${res.has_audio ? ' 🔊' : ' ⚠️ (Audio akan digabung)'}`;
        resolutionSelect.appendChild(option);
    });

    document.getElementById('resolution-container').style.display = 'block';
}


function fetchVideo() {
    const url = document.getElementById('video-url').value.trim();
    const formatId = document.getElementById('resolution-select').value;

    if (!formatId) {
        alert("Pilih resolusi terlebih dahulu!");
        return;
    }

    fetch('/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, format_id: formatId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        alert(`Download Berhasil! File: ${data.file_path}`);
    })
    .catch(error => {
        alert(`Gagal: ${error.message}`);
    });
}