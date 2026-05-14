document.addEventListener('DOMContentLoaded', () => {
    const drawBtn = document.getElementById('draw-btn');
    const redrawBtn = document.getElementById('redraw-btn');
    const welcomeScreen = document.getElementById('welcome-screen');
    const resultScreen = document.getElementById('result-screen');

    // Result elements
    const resName = document.getElementById('res-name');
    const resImage = document.getElementById('res-image');
    const resRating = document.getElementById('res-rating');
    const resReviews = document.getElementById('res-reviews');
    const resAddress = document.getElementById('res-address');
    const resHours = document.getElementById('res-hours');
    const resMapsBtn = document.getElementById('res-maps-btn');

    async function drawRandomRestaurant() {
        // Show loading state
        const originalText = drawBtn.innerHTML;
        drawBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> 抽取中...';
        drawBtn.classList.add('loading-pulse');
        
        if (redrawBtn) {
            redrawBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> 抽取中...';
            redrawBtn.disabled = true;
        }

        try {
            // Give a slight delay to simulate a real "drawing" feeling
            await new Promise(r => setTimeout(r, 800));

            const response = await fetch('/api/random');
            const data = await response.json();

            if (data.status === 'success') {
                const r = data.data;
                resName.textContent = r.name;
                resImage.src = r.photo_url || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4';
                resRating.textContent = r.rating || 'N/A';
                resReviews.textContent = r.user_ratings_total || '0';
                resAddress.textContent = r.address || '無地址資訊';
                resHours.textContent = r.open_hours || '未提供營業時間';
                
                // Construct Google Maps Search URL
                const encodedName = encodeURIComponent(r.name + ' ' + (r.address || ''));
                resMapsBtn.href = `https://www.google.com/maps/search/?api=1&query=${encodedName}`;

                // Switch screens
                welcomeScreen.classList.add('d-none');
                resultScreen.classList.remove('d-none');
            } else {
                alert('找不到餐廳，請稍後再試！');
            }
        } catch (error) {
            console.error('Error fetching random restaurant:', error);
            alert('發生錯誤，請稍後再試！');
        } finally {
            drawBtn.innerHTML = originalText;
            drawBtn.classList.remove('loading-pulse');
            if (redrawBtn) {
                redrawBtn.innerHTML = '<i class="fa-solid fa-rotate-right me-2"></i> 再抽一次';
                redrawBtn.disabled = false;
            }
        }
    }

    if (drawBtn) {
        drawBtn.addEventListener('click', drawRandomRestaurant);
    }
    
    if (redrawBtn) {
        redrawBtn.addEventListener('click', drawRandomRestaurant);
    }
});
