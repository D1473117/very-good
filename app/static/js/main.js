document.addEventListener('DOMContentLoaded', () => {
    const budgetSlider = document.getElementById('budget-slider');
    const budgetVal = document.getElementById('budget-val');
    const distanceSlider = document.getElementById('distance-slider');
    const distanceVal = document.getElementById('distance-val');
    
    const btnLocate = document.getElementById('btn-locate');
    const locationText = document.getElementById('location-text');
    
    const btnRecommend = document.getElementById('btn-recommend');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    
    const resultCard = document.getElementById('result-card');
    const slotOverlay = document.getElementById('slot-overlay');
    const slotNames = document.getElementById('slot-names');
    
    let userLat = null;
    let userLng = null;
    
    // Update sliders
    budgetSlider.addEventListener('input', (e) => {
        budgetVal.textContent = e.target.value;
    });
    
    distanceSlider.addEventListener('input', (e) => {
        distanceVal.textContent = e.target.value + ' km';
    });
    
    // Geolocation
    btnLocate.addEventListener('click', () => {
        locationText.textContent = '定位中...';
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    userLat = position.coords.latitude;
                    userLng = position.coords.longitude;
                    locationText.textContent = `${userLat.toFixed(4)}, ${userLng.toFixed(4)}`;
                    locationText.classList.remove('text-white-50');
                    locationText.classList.add('text-success');
                },
                (error) => {
                    console.error("Error getting location:", error);
                    locationText.textContent = '定位失敗，將使用全域搜尋';
                }
            );
        } else {
            locationText.textContent = '您的瀏覽器不支援定位功能';
        }
    });
    
    // Recommend Action
    btnRecommend.addEventListener('click', async () => {
        // UI Loading
        btnText.classList.add('d-none');
        btnSpinner.classList.remove('d-none');
        resultCard.classList.add('d-none');
        
        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    lat: userLat,
                    lng: userLng,
                    budget: parseInt(budgetSlider.value),
                    distance: parseFloat(distanceSlider.value)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                playSlotAnimation(data.data);
            } else {
                alert(data.message || '找不到符合條件的餐廳');
                btnText.classList.remove('d-none');
                btnSpinner.classList.add('d-none');
            }
        } catch (error) {
            console.error('API Error:', error);
            alert('系統發生錯誤，請稍後再試！');
            btnText.classList.remove('d-none');
            btnSpinner.classList.add('d-none');
        }
    });
    
    function playSlotAnimation(restaurantData) {
        // Reset slot overlay
        slotOverlay.classList.remove('d-none');
        slotNames.innerHTML = '';
        slotNames.style.transition = 'none';
        slotNames.style.top = '0px';
        
        // Generate fake names for animation
        const fakes = ['麥當勞', '肯德基', '鼎泰豐', '巷口陽春麵', '不知道吃啥', '吃土吧', '隨便', '都可以', '便當店', '火鍋店'];
        let itemsHTML = '';
        
        for(let i=0; i<20; i++) {
            const name = fakes[Math.floor(Math.random() * fakes.length)];
            itemsHTML += `<div class="slot-item">${name}</div>`;
        }
        // Last item is the actual result
        itemsHTML += `<div class="slot-item text-warning">${restaurantData.name}</div>`;
        slotNames.innerHTML = itemsHTML;
        
        // Trigger animation
        setTimeout(() => {
            slotNames.style.transition = 'top 3s cubic-bezier(0.1, 0.8, 0.2, 1)';
            slotNames.style.top = `-${20 * 100}px`; // Scroll to the 21st item
        }, 50);
        
        // After animation
        setTimeout(() => {
            slotOverlay.classList.add('d-none');
            showResult(restaurantData);
            
            // Restore button
            btnText.classList.remove('d-none');
            btnSpinner.classList.add('d-none');
        }, 3200);
    }
    
    function showResult(data) {
        document.getElementById('result-name').textContent = data.name;
        document.getElementById('result-category').innerHTML = `<i class="bi bi-tag-fill"></i> ${data.category}`;
        document.getElementById('result-rating').innerHTML = `<i class="bi bi-star-fill text-warning"></i> ${data.rating}`;
        
        let budgetStr = '';
        for(let i=0; i<data.budget_level; i++) budgetStr += '$';
        document.getElementById('result-budget').innerHTML = `<i class="bi bi-currency-dollar text-success"></i> ${budgetStr}`;
        
        document.getElementById('result-map-link').href = data.google_maps_url;
        
        resultCard.classList.remove('d-none');
    }
});
