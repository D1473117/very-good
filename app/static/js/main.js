document.addEventListener('DOMContentLoaded', () => {
    // --- Explore Tab Elements ---
    const budgetSlider = document.getElementById('budget-slider');
    const budgetVal = document.getElementById('budget-val');
    const distanceSlider = document.getElementById('distance-slider');
    const distanceVal = document.getElementById('distance-val');
    const btnLocate = document.getElementById('btn-locate');
    const locationText = document.getElementById('location-text');
    const selectLandmark = document.getElementById('select-landmark');
    const btnRecommend = document.getElementById('btn-recommend');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const resultCard = document.getElementById('result-card');
    const slotOverlay = document.getElementById('slot-overlay');
    const slotNames = document.getElementById('slot-names');
    
    // Heart Favorite Toggle on Result Card
    const btnFavoriteToggle = document.getElementById('btn-favorite-toggle');
    const heartIcon = document.getElementById('heart-icon');
    
    // Advanced Filters
    const btnAdvancedToggle = document.getElementById('btn-advanced-toggle');
    const advancedFiltersPanel = document.getElementById('advanced-filters');
    const ratingSlider = document.getElementById('rating-slider');
    const ratingVal = document.getElementById('rating-val');
    const switchFavorites = document.getElementById('switch-favorites');
    const categoryCheckboxes = document.getElementById('category-checkboxes');
    
    // --- Bottom Navigation & Tabs ---
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // --- Favorites Tab Elements ---
    const favoritesList = document.getElementById('favorites-list');
    const btnAddCustomToggle = document.getElementById('btn-add-custom-toggle');
    const customRestaurantForm = document.getElementById('custom-restaurant-form');
    const btnCustomCancel = document.getElementById('btn-custom-cancel');
    const btnCustomSubmit = document.getElementById('btn-custom-submit');
    const customNameInput = document.getElementById('custom-name');
    const customCategoryInput = document.getElementById('custom-category');
    const customBudgetSelect = document.getElementById('custom-budget');
    const customMapUrlInput = document.getElementById('custom-map-url');
    
    // --- History Tab Elements ---
    const historyList = document.getElementById('history-list');
    
    // --- State Variables ---
    let userLat = null;
    let userLng = null;
    let currentRecommendedId = null;
    let currentRecommendedData = null;
    let excludedCategories = new Set();
    let allCategories = [];

    // ==========================================
    // 1. TABS NAVIGATION & INITIALIZATION
    // ==========================================
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            
            // Update active nav state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Switch visible tab
            tabContents.forEach(content => {
                content.classList.add('d-none');
                if (content.id === `tab-${targetTab}`) {
                    content.classList.remove('d-none');
                }
            });
            
            // Fetch tab specific data
            if (targetTab === 'favorites') {
                fetchFavorites();
            } else if (targetTab === 'history') {
                fetchHistory();
            } else if (targetTab === 'explore') {
                fetchCategories();
            }
        });
    });

    // Initial Load Categories
    fetchCategories();

    // ==========================================
    // 2. EXPLORE: SLIDERS & ADVANCED FILTERS
    // ==========================================
    
    budgetSlider.addEventListener('input', (e) => {
        budgetVal.textContent = e.target.value;
    });
    
    distanceSlider.addEventListener('input', (e) => {
        distanceVal.textContent = e.target.value + ' km';
    });

    ratingSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        ratingVal.innerHTML = `${val.toFixed(1)} <i class="bi bi-star-fill"></i>`;
    });

    // Advanced Filters Expand Toggle
    btnAdvancedToggle.addEventListener('click', () => {
        const isHidden = advancedFiltersPanel.classList.contains('d-none');
        if (isHidden) {
            advancedFiltersPanel.classList.remove('d-none');
            btnAdvancedToggle.innerHTML = '<i class="bi bi-sliders2-vertical"></i> 收起防雷篩選 <i class="bi bi-chevron-up"></i>';
        } else {
            advancedFiltersPanel.classList.add('d-none');
            btnAdvancedToggle.innerHTML = '<i class="bi bi-sliders2-vertical"></i> 進階防雷篩選 <i class="bi bi-chevron-down"></i>';
        }
    });

    // Dynamic categories fetching for exclusion
    async function fetchCategories() {
        try {
            const response = await fetch('/api/categories');
            const res = await response.json();
            if (res.success) {
                allCategories = res.data;
                renderCategoryExclusions();
            }
        } catch (err) {
            console.error('Failed to load categories', err);
        }
    }

    function renderCategoryExclusions() {
        if (!categoryCheckboxes) return;
        categoryCheckboxes.innerHTML = '';
        if (allCategories.length === 0) {
            categoryCheckboxes.innerHTML = '<span class="text-white-50 small">尚無餐廳分類數據</span>';
            return;
        }

        allCategories.forEach(cat => {
            const badge = document.createElement('span');
            badge.className = 'category-badge';
            if (excludedCategories.has(cat)) {
                badge.classList.add('excluded');
            }
            badge.textContent = cat;
            badge.addEventListener('click', () => {
                if (excludedCategories.has(cat)) {
                    excludedCategories.delete(cat);
                    badge.classList.remove('excluded');
                } else {
                    excludedCategories.add(cat);
                    badge.classList.add('excluded');
                }
            });
            categoryCheckboxes.appendChild(badge);
        });
    }

    // Geolocation
    btnLocate.addEventListener('click', () => {
        locationText.textContent = '定位中...';
        // Reset manual dropdown when using GPS
        if (selectLandmark) selectLandmark.value = '';
        
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
                    locationText.classList.remove('text-success');
                    locationText.classList.add('text-white-50');
                }
            );
        } else {
            locationText.textContent = '您的瀏覽器不支援定位功能';
        }
    });

    // Landmark Selector Event
    if (selectLandmark) {
        selectLandmark.addEventListener('change', (e) => {
            const val = e.target.value;
            if (val) {
                const parts = val.split(',');
                userLat = parseFloat(parts[0]);
                userLng = parseFloat(parts[1]);
                const selectedText = e.target.options[e.target.selectedIndex].text;
                locationText.textContent = `手動地標：${selectedText}`;
                locationText.classList.remove('text-white-50');
                locationText.classList.add('text-success');
            } else {
                userLat = null;
                userLng = null;
                locationText.textContent = '尚未取得位置，可點擊定位或從下方選擇';
                locationText.classList.remove('text-success');
                locationText.classList.add('text-white-50');
            }
        });
    }

    // ==========================================
    // 3. EXPLORE: RECOMMEND ACTION
    // ==========================================
    
    btnRecommend.addEventListener('click', async () => {
        btnText.classList.add('d-none');
        btnSpinner.classList.remove('d-none');
        resultCard.classList.add('d-none');
        
        try {
            const payload = {
                lat: userLat,
                lng: userLng,
                budget: parseInt(budgetSlider.value),
                distance: parseFloat(distanceSlider.value),
                min_rating: parseFloat(ratingSlider.value),
                categories_exclude: Array.from(excludedCategories),
                only_favorites: switchFavorites.checked
            };

            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
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
        slotOverlay.classList.remove('d-none');
        slotNames.innerHTML = '';
        slotNames.style.transition = 'none';
        slotNames.style.top = '0px';
        
        const fakes = ['麥當勞', '肯德基', '鼎泰豐', '巷口陽春麵', '不知道吃啥', '吃土吧', '隨便', '都可以', '便當店', '火鍋店', '薩莉亞', '星巴克', '壽司郎', '吉野家'];
        let itemsHTML = '';
        
        for(let i=0; i<20; i++) {
            const name = fakes[Math.floor(Math.random() * fakes.length)];
            itemsHTML += `<div class="slot-item">${name}</div>`;
        }
        itemsHTML += `<div class="slot-item text-warning">${restaurantData.name}</div>`;
        slotNames.innerHTML = itemsHTML;
        
        setTimeout(() => {
            slotNames.style.transition = 'top 3s cubic-bezier(0.1, 0.8, 0.2, 1)';
            slotNames.style.top = `-${20 * 120}px`; // 配合 style.css 中的 .slot-item 高度 120px
        }, 50);
        
        setTimeout(() => {
            slotOverlay.classList.add('d-none');
            showResult(restaurantData);
            btnText.classList.remove('d-none');
            btnSpinner.classList.add('d-none');
        }, 3200);
    }
    
    function showResult(data) {
        currentRecommendedId = data.id;
        currentRecommendedData = data;
        
        document.getElementById('result-name').textContent = data.name;
        document.getElementById('result-category').innerHTML = `<i class="bi bi-tag-fill"></i> ${data.category}`;
        document.getElementById('result-rating').innerHTML = `<i class="bi bi-star-fill text-warning"></i> ${data.rating ? data.rating.toFixed(1) : '5.0'}`;
        
        let budgetStr = '';
        for(let i=0; i<data.budget_level; i++) budgetStr += '$';
        document.getElementById('result-budget').innerHTML = `<i class="bi bi-currency-dollar text-success"></i> ${budgetStr}`;
        
        document.getElementById('result-map-link').href = data.google_maps_url;
        
        // Favorite Heart state
        updateHeartUI(data.is_favorite);
        
        resultCard.classList.remove('d-none');
    }

    // Heart toggler event
    btnFavoriteToggle.addEventListener('click', async () => {
        if (!currentRecommendedId) return;
        
        try {
            const response = await fetch('/api/favorites/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ restaurant_id: currentRecommendedId })
            });
            const res = await response.json();
            if (res.success) {
                updateHeartUI(res.is_favorite);
                if (currentRecommendedData) {
                    currentRecommendedData.is_favorite = res.is_favorite;
                }
            }
        } catch (err) {
            console.error('Error toggling favorite', err);
        }
    });

    function updateHeartUI(isFav) {
        if (isFav) {
            btnFavoriteToggle.classList.add('active');
            heartIcon.className = 'bi bi-heart-fill text-danger';
        } else {
            btnFavoriteToggle.classList.remove('active');
            heartIcon.className = 'bi bi-heart text-white-50';
        }
    }

    // ==========================================
    // 4. FAVORITES TAB LOGIC
    // ==========================================
    
    // Toggle add custom form
    btnAddCustomToggle.addEventListener('click', () => {
        customRestaurantForm.classList.remove('d-none');
        customRestaurantForm.scrollIntoView({ behavior: 'smooth' });
    });

    btnCustomCancel.addEventListener('click', () => {
        customRestaurantForm.classList.add('d-none');
        clearCustomForm();
    });

    function clearCustomForm() {
        customNameInput.value = '';
        customCategoryInput.value = '';
        customBudgetSelect.value = '1';
        customMapUrlInput.value = '';
    }

    btnCustomSubmit.addEventListener('click', async () => {
        const name = customNameInput.value.trim();
        const category = customCategoryInput.value.trim();
        const budget = parseInt(customBudgetSelect.value);
        const mapUrl = customMapUrlInput.value.trim();

        if (!name || !category) {
            alert('餐廳名稱與分類是必填欄位喔！');
            return;
        }

        try {
            const payload = {
                name: name,
                category: category,
                budget_level: budget,
                google_maps_url: mapUrl
            };

            const response = await fetch('/api/restaurants/custom', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const res = await response.json();
            if (res.success) {
                alert(res.message);
                customRestaurantForm.classList.add('d-none');
                clearCustomForm();
                fetchFavorites(); // Reload list
                fetchCategories(); // Update exclusion filter categories list
            } else {
                alert(res.message || '新增私房菜失敗');
            }
        } catch (err) {
            console.error('Error adding custom restaurant', err);
            alert('系統發生錯誤！');
        }
    });

    async function fetchFavorites() {
        favoritesList.innerHTML = `
            <div class="text-center py-4 text-white-50">
                <div class="spinner-border spinner-border-sm text-warning mb-2" role="status"></div>
                <p class="m-0">讀取口袋名單中...</p>
            </div>
        `;
        try {
            const response = await fetch('/api/favorites');
            const res = await response.json();
            if (res.success) {
                renderFavorites(res.data);
            } else {
                favoritesList.innerHTML = `<p class="text-center text-white-50 py-3">載入收藏清單失敗: ${res.message}</p>`;
            }
        } catch (err) {
            console.error('Error fetching favorites', err);
            favoritesList.innerHTML = `<p class="text-center text-white-50 py-3">網路連線異常，請稍後再試</p>`;
        }
    }

    function renderFavorites(favs) {
        favoritesList.innerHTML = '';
        if (favs.length === 0) {
            favoritesList.innerHTML = `
                <div class="text-center py-5 text-white-50 glass-card">
                    <i class="bi bi-heartbreak-fill fs-2 text-white-50 mb-2"></i>
                    <p class="mb-0">口袋名單空空如也，點擊抽籤卡片的心形，或主動新增私房餐館吧！</p>
                </div>
            `;
            return;
        }

        favs.forEach(item => {
            const card = document.createElement('div');
            card.className = 'fav-item-card d-flex justify-content-between align-items-center';
            
            let budgetStr = '';
            for(let i=0; i<item.budget_level; i++) budgetStr += '$';
            
            const isCustomTag = item.is_custom ? '<span class="custom-badge ms-2">私房</span>' : '';

            card.innerHTML = `
                <div>
                    <h5 class="fw-bold text-white mb-1 d-flex align-items-center">${item.name} ${isCustomTag}</h5>
                    <div class="small text-white-50 d-flex gap-2 align-items-center">
                        <span><i class="bi bi-tag-fill text-warning"></i> ${item.category}</span>
                        <span>•</span>
                        <span><i class="bi bi-star-fill text-warning"></i> ${item.rating ? item.rating.toFixed(1) : '5.0'}</span>
                        <span>•</span>
                        <span class="text-success fw-bold">${budgetStr}</span>
                    </div>
                </div>
                <div class="d-flex gap-2">
                    <a href="${item.google_maps_url}" target="_blank" class="btn btn-sm btn-outline-light rounded-circle" title="開啟地圖"><i class="bi bi-map-fill"></i></a>
                    <button class="btn btn-sm btn-outline-danger rounded-circle btn-fav-delete" data-id="${item.id}" title="移除收藏"><i class="bi bi-trash3-fill"></i></button>
                </div>
            `;

            // Delete event
            card.querySelector('.btn-fav-delete').addEventListener('click', async (e) => {
                const id = e.currentTarget.getAttribute('data-id');
                if (confirm(`確定要將「${item.name}」移出口袋名單嗎？`)) {
                    try {
                        const response = await fetch('/api/favorites/toggle', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ restaurant_id: id })
                        });
                        const res = await response.json();
                        if (res.success) {
                            fetchFavorites(); // Reload
                            // If this was the recommended one on screen, update heart to hollow
                            if (currentRecommendedId == id) {
                                updateHeartUI(false);
                                if (currentRecommendedData) currentRecommendedData.is_favorite = false;
                            }
                        }
                    } catch (err) {
                        console.error('Delete favorite error', err);
                    }
                }
            });

            favoritesList.appendChild(card);
        });
    }

    // ==========================================
    // 5. JOURNAL/HISTORY TAB LOGIC
    // ==========================================
    
    async function fetchHistory() {
        historyList.innerHTML = `
            <div class="text-center py-4 text-white-50">
                <div class="spinner-border spinner-border-sm text-warning mb-2" role="status"></div>
                <p class="m-0">讀取探險紀錄中...</p>
            </div>
        `;
        try {
            const response = await fetch('/api/history');
            const res = await response.json();
            if (res.success) {
                renderHistory(res.data);
            } else {
                historyList.innerHTML = `<p class="text-center text-white-50 py-3">載入探險紀錄失敗: ${res.message}</p>`;
            }
        } catch (err) {
            console.error('Error fetching history', err);
            historyList.innerHTML = `<p class="text-center text-white-50 py-3">網路連線異常，請稍後再試</p>`;
        }
    }

    function renderHistory(historyData) {
        historyList.innerHTML = '';
        if (historyData.length === 0) {
            historyList.innerHTML = `
                <div class="text-center py-5 text-white-50 glass-card">
                    <i class="bi bi-clock-history fs-2 text-white-50 mb-2"></i>
                    <p class="mb-0">您還沒有進行過美食抽籤喔，快去首頁探索您的第一餐吧！</p>
                </div>
            `;
            return;
        }

        historyData.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-item-card';

            const formattedDate = new Date(item.created_at).toLocaleString('zh-TW', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            // Star Rating Logic Helper
            const rating = item.user_rating || 0;
            let starsHTML = '';
            for (let i = 1; i <= 5; i++) {
                const starClass = i <= rating ? 'bi-star-fill active' : 'bi-star';
                starsHTML += `<i class="bi ${starClass}" data-value="${i}"></i>`;
            }

            card.innerHTML = `
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <h5 class="fw-bold text-white mb-1">${item.restaurant_name}</h5>
                        <div class="small text-white-50">
                            <span><i class="bi bi-clock"></i> ${formattedDate}</span>
                            <span class="mx-1">•</span>
                            <span>${item.category || '分類未明'}</span>
                        </div>
                    </div>
                    <div class="d-flex gap-1">
                        <a href="${item.google_maps_url || '#'}" target="_blank" class="btn btn-sm btn-outline-light rounded-circle" title="開啟地圖"><i class="bi bi-map-fill"></i></a>
                        <button class="btn btn-sm btn-outline-danger rounded-circle btn-history-delete" data-id="${item.id}" title="刪除紀錄"><i class="bi bi-trash3-fill"></i></button>
                    </div>
                </div>
                
                <!-- Feedback Section -->
                <div class="glass-card mt-3 p-2 py-3 bg-black bg-opacity-20 border-0">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="small text-warning fw-bold"><i class="bi bi-chat-heart"></i> 給予美食評價：</span>
                        <div class="star-rating" data-history-id="${item.id}">
                            ${starsHTML}
                        </div>
                    </div>
                    <div class="input-group input-group-sm mt-2">
                        <input type="text" class="form-control glass-input py-1 text-white border-0 bg-white bg-opacity-5" placeholder="寫些心得筆記吧 (如: 份量超大)..." value="${item.comment || ''}">
                        <button class="btn btn-warning btn-save-feedback rounded-end px-3" data-id="${item.id}"><i class="bi bi-check-lg"></i> 儲存</button>
                    </div>
                </div>
            `;

            // Star Rating Clicks
            const stars = card.querySelectorAll('.star-rating i');
            let selectedRating = rating;

            stars.forEach(star => {
                star.addEventListener('click', async (e) => {
                    const value = parseInt(star.getAttribute('data-value'));
                    selectedRating = value;
                    
                    // Update star colors instantly
                    stars.forEach((s, idx) => {
                        if (idx < value) {
                            s.className = 'bi bi-star-fill active';
                        } else {
                            s.className = 'bi bi-star';
                        }
                    });

                    // Auto submit star rating
                    await submitFeedback(item.id, selectedRating, card.querySelector('input').value.trim());
                });
            });

            // Save Comments Button
            card.querySelector('.btn-save-feedback').addEventListener('click', async () => {
                const commentText = card.querySelector('input').value.trim();
                await submitFeedback(item.id, selectedRating, commentText);
            });

            // Delete History Item
            card.querySelector('.btn-history-delete').addEventListener('click', async () => {
                if (confirm(`要刪除這筆在「${item.restaurant_name}」的抽籤紀錄嗎？`)) {
                    try {
                        const response = await fetch(`/api/history/${item.id}`, { method: 'DELETE' });
                        const res = await response.json();
                        if (res.success) {
                            fetchHistory(); // Reload
                        }
                    } catch (err) {
                        console.error('Error deleting history', err);
                    }
                }
            });

            historyList.appendChild(card);
        });
    }

    async function submitFeedback(historyId, rating, comment) {
        if (rating === 0) {
            alert('請點擊星星給予 1-5 顆星的美食評分喔！');
            return;
        }

        try {
            const response = await fetch(`/api/history/${historyId}/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_rating: rating, comment: comment })
            });
            const res = await response.json();
            if (!res.success) {
                alert(res.message || '回饋失敗，請稍後再試！');
            }
        } catch (err) {
            console.error('Error submitting feedback', err);
        }
    }
});
