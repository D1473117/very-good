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
    
    // Advanced features result elements
    const resCategoryBadge = document.getElementById('res-category-badge');
    const resPriceText = document.getElementById('res-price-text');
    const favoriteBtn = document.getElementById('favorite-btn');
    const reviewsList = document.getElementById('restaurant-reviews-list');
    const submitReviewBtn = document.getElementById('submit-review-btn');
    const reviewComment = document.getElementById('review-comment');

    // New Upgraded elements for Restaurant Info display
    const resStatusBadge = document.getElementById('res-status-badge');
    const resDistanceBadge = document.getElementById('res-distance-badge');
    const resPriceGauge = document.getElementById('res-price-gauge');
    const resSignatureTags = document.getElementById('res-signature-tags');
    const resSignatureBox = document.getElementById('res-signature-box');

    // GPS / Distance State & Logic
    let userLocation = null;

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                console.log("GPS Location acquired successfully:", userLocation);
            },
            (error) => {
                console.log("GPS Location permission denied or unavailable. Using Taipei 101 fallback center.");
                userLocation = {
                    lat: 25.033964,
                    lng: 121.564468
                };
            }
        );
    }

    // Haversine formula to compute distance and multi-modal travel estimation
    function calculateDistanceAndTravel(lat2, lon2) {
        const lat1 = userLocation ? userLocation.lat : 25.033964;
        const lon1 = userLocation ? userLocation.lng : 121.564468;

        const R = 6371e3; // Earth radius in meters
        const phi1 = lat1 * Math.PI / 180;
        const phi2 = lat2 * Math.PI / 180;
        const deltaPhi = (lat2 - lat1) * Math.PI / 180;
        const deltaLambda = (lon2 - lon1) * Math.PI / 180;

        const a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
                  Math.cos(phi1) * Math.cos(phi2) *
                  Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        const distance = R * c;

        let distanceText = "";
        if (distance < 1000) {
            distanceText = `距離 ${Math.round(distance)} 公尺`;
        } else {
            distanceText = `距離 ${(distance / 1000).toFixed(1)} 公里`;
        }

        // Walking speed ~ 5 km/h => 83 meters/minute
        // Riding speed ~ 30 km/h => 500 meters/minute
        const walkingTime = Math.max(1, Math.round(distance / 83));
        const ridingTime = Math.max(1, Math.round(distance / 500));

        const isMock = !userLocation;
        const mockBadge = isMock ? ' <span class="badge bg-secondary bg-opacity-10 text-secondary border-0 ms-1 px-1.5 py-0.5" style="font-size: 0.65rem; font-weight: normal;">示範距離</span>' : '';

        return {
            distanceText: distanceText + mockBadge,
            travelHtml: `
                <i class="fa-solid fa-person-walking text-primary me-1"></i> 步行約 ${walkingTime} 分鐘 
                <span class="mx-1 text-muted">|</span> 
                <i class="fa-solid fa-motorcycle text-primary me-1"></i> 騎車約 ${ridingTime} 分鐘
            `
        };
    }

    // Dynamic Business Status Parser with Closing Countdown
    function parseBusinessStatus(openHoursStr) {
        if (!openHoursStr || openHoursStr === '未提供營業時間') {
            return {
                status: 'closed',
                badgeClass: 'status-badge-closed',
                text: '○ 暫無營業資訊'
            };
        }
        
        if (openHoursStr.includes('24 小時') || openHoursStr.includes('24小時')) {
            return {
                status: 'open',
                badgeClass: 'status-badge-open',
                text: '● 24 小時營業中'
            };
        }

        const timeMatch = openHoursStr.match(/(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})/);
        if (!timeMatch) {
            return {
                status: 'open',
                badgeClass: 'status-badge-open',
                text: '● ' + openHoursStr
            };
        }

        const startH = parseInt(timeMatch[1], 10);
        const startM = parseInt(timeMatch[2], 10);
        const endH = parseInt(timeMatch[3], 10);
        const endM = parseInt(timeMatch[4], 10);

        const now = new Date();
        const currH = now.getHours();
        const currM = now.getMinutes();

        const startMinutes = startH * 60 + startM;
        let endMinutes = endH * 60 + endM;
        const currMinutes = currH * 60 + currM;

        let isOpen = false;
        let minutesLeft = 9999;

        if (endMinutes < startMinutes) {
            // Crosses midnight e.g. 11:00 - 04:00
            if (currMinutes >= startMinutes) {
                isOpen = true;
                minutesLeft = (24 * 60 - currMinutes) + endMinutes;
            } else if (currMinutes < endMinutes) {
                isOpen = true;
                minutesLeft = endMinutes - currMinutes;
            } else {
                isOpen = false;
            }
        } else {
            // Same day e.g. 11:00 - 21:00
            if (currMinutes >= startMinutes && currMinutes < endMinutes) {
                isOpen = true;
                minutesLeft = endMinutes - currMinutes;
            } else {
                isOpen = false;
            }
        }

        if (isOpen) {
            if (minutesLeft <= 60) {
                return {
                    status: 'closing',
                    badgeClass: 'status-badge-closing',
                    text: `● 即將打烊 (剩 ${minutesLeft} 分)`
                };
            } else {
                return {
                    status: 'open',
                    badgeClass: 'status-badge-open',
                    text: '● 營業中'
                };
            }
        } else {
            return {
                status: 'closed',
                badgeClass: 'status-badge-closed',
                text: '○ 已打烊'
            };
        }
    }

    // Render Price Gauge with Active/Inactive icons
    function renderPriceGauge(priceLevel) {
        let gaugeHtml = '';
        for (let i = 1; i <= 4; i++) {
            gaugeHtml += i <= priceLevel 
                ? '<i class="fa-solid fa-dollar-sign price-active" style="font-size:0.75rem;"></i>' 
                : '<i class="fa-solid fa-dollar-sign price-inactive" style="font-size:0.75rem;"></i>';
        }
        return gaugeHtml;
    }

    // Render Signature Menu Tags
    function renderSignatureTags(signatureStr, tagsContainer, boxContainer) {
        if (!tagsContainer || !boxContainer) return;
        if (signatureStr) {
            tagsContainer.innerHTML = '';
            const items = signatureStr.split(/[、,]/).map(item => item.trim()).filter(item => item.length > 0);
            items.forEach(item => {
                tagsContainer.innerHTML += `<span class="signature-tag"><i class="fa-solid fa-utensils me-1 opacity-70" style="font-size:0.7rem;"></i>${item}</span>`;
            });
            boxContainer.classList.remove('d-none');
        } else {
            boxContainer.classList.add('d-none');
        }
    }

    // Helper: render star icons
    function renderStars(rating) {
        let starsHtml = '';
        for (let i = 1; i <= 5; i++) {
            starsHtml += i <= rating 
                ? '<i class="fa-solid fa-star text-warning small"></i>' 
                : '<i class="fa-regular fa-star text-secondary text-opacity-30 small"></i>';
        }
        return starsHtml;
    }

    // Helper: render review items
    function renderReviews(reviews) {
        if (!reviewsList) return;
        reviewsList.innerHTML = '';
        
        if (reviews && reviews.length > 0) {
            reviews.forEach(rv => {
                reviewsList.innerHTML += `
                    <div class="review-item py-2 border-bottom border-secondary border-opacity-10">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <strong class="text-dark small"><i class="fa-regular fa-user me-1 text-muted"></i>${rv.username}</strong>
                            <span class="text-muted small" style="font-size: 0.75rem;">${rv.created_at}</span>
                        </div>
                        <div class="mb-1">${renderStars(rv.rating)}</div>
                        <p class="text-secondary mb-0 small" style="line-height:1.4;">${rv.comment || '（無文字評語）'}</p>
                    </div>
                `;
            });
        } else {
            reviewsList.innerHTML = '<div class="text-center text-muted small py-4"><i class="fa-regular fa-comments me-1"></i> 目前尚無這家餐廳的饕客評語，快來發表第一篇吧！</div>';
        }
    }

    async function drawRandomRestaurant() {
        // Show loading state
        const originalText = drawBtn ? drawBtn.innerHTML : '';
        if (drawBtn) {
            drawBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> 正在努力篩選中...';
            drawBtn.classList.add('loading-pulse');
            drawBtn.disabled = true;
        }
        
        if (redrawBtn) {
            redrawBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> 抽取中...';
            redrawBtn.disabled = true;
        }

        // Get filter criteria values
        const category = document.getElementById('filter-category')?.value || 'all';
        const priceLevel = document.getElementById('filter-price')?.value || 'all';
        const minRating = document.getElementById('filter-rating')?.value || 'all';

        try {
            // Give a slight delay to simulate a real "drawing" feeling
            await new Promise(r => setTimeout(r, 800));

            const response = await fetch(`/api/random?category=${encodeURIComponent(category)}&price_level=${encodeURIComponent(priceLevel)}&min_rating=${encodeURIComponent(minRating)}`);
            const data = await response.json();

            if (data.status === 'success') {
                const r = data.data;
                
                // Populate results
                if (resName) resName.textContent = r.name;
                if (resImage) resImage.src = r.photo_url || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4';
                if (resRating) resRating.textContent = r.rating || 'N/A';
                if (resReviews) resReviews.textContent = r.user_ratings_total || '0';
                if (resAddress) resAddress.textContent = r.address || '無地址資訊';
                if (resHours) resHours.textContent = r.open_hours || '未提供營業時間';
                
                if (resCategoryBadge) resCategoryBadge.textContent = r.category || '未分類';
                
                if (resPriceText) {
                    const p = r.price_level;
                    resPriceText.textContent = p === 1 ? '平價餐點' : p === 2 ? '中等價位' : p === 3 ? '高檔享受' : '奢華饗宴';
                }

                // Render upgraded visual elements (Status, Distance, Price Gauge, Signature Tags)
                if (resStatusBadge) {
                    const statusObj = parseBusinessStatus(r.open_hours);
                    resStatusBadge.className = `badge rounded-pill px-3 py-2 fw-bold fs-7 shadow-sm ${statusObj.badgeClass}`;
                    resStatusBadge.innerHTML = statusObj.text;
                }

                if (resDistanceBadge) {
                    const distObj = calculateDistanceAndTravel(r.latitude, r.longitude);
                    resDistanceBadge.innerHTML = `<i class="fa-solid fa-location-crosshairs text-primary me-1"></i> ${distObj.distanceText} <span class="mx-1 text-muted">|</span> ${distObj.travelHtml}`;
                }

                if (resPriceGauge) {
                    resPriceGauge.innerHTML = renderPriceGauge(r.price_level);
                }

                if (resSignatureTags && resSignatureBox) {
                    renderSignatureTags(r.signature, resSignatureTags, resSignatureBox);
                }

                if (favoriteBtn) {
                    favoriteBtn.dataset.restaurantId = r.id;
                    const heartIcon = favoriteBtn.querySelector('.heart-icon');
                    if (heartIcon) {
                        if (r.is_favorited) {
                            heartIcon.className = 'fa-solid fa-heart heart-icon text-danger';
                        } else {
                            heartIcon.className = 'fa-regular fa-heart heart-icon';
                        }
                    }
                }

                // Render reviews
                renderReviews(data.reviews);
                
                // Construct Google Maps Search URL
                const encodedName = encodeURIComponent(r.name + ' ' + (r.address || ''));
                if (resMapsBtn) resMapsBtn.href = `https://www.google.com/maps/search/?api=1&query=${encodedName}`;

                // Switch screens
                if (welcomeScreen) welcomeScreen.classList.add('d-none');
                if (resultScreen) {
                    resultScreen.classList.remove('d-none');
                    resultScreen.classList.add('animate-fade-in');
                }
            } else {
                alert(data.message || '找不到符合條件的餐廳，請調整篩選條件再試一次！');
            }
        } catch (error) {
            console.error('Error fetching random restaurant:', error);
            alert('發生錯誤，請稍後再試！');
        } finally {
            if (drawBtn) {
                drawBtn.innerHTML = originalText;
                drawBtn.classList.remove('loading-pulse');
                drawBtn.disabled = false;
            }
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

    // ----------------- AJAX Favorite Heart Toggle Handler -----------------
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', async () => {
            const restaurantId = favoriteBtn.dataset.restaurantId;
            if (!restaurantId) return;

            try {
                const response = await fetch('/api/favorites/toggle', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ restaurant_id: restaurantId })
                });

                if (response.status === 401) {
                    alert('請先登入帳號以使用收藏功能！');
                    window.location.href = '/login';
                    return;
                }

                const data = await response.json();
                if (data.status === 'success') {
                    const heartIcon = favoriteBtn.querySelector('.heart-icon');
                    if (heartIcon) {
                        if (data.is_favorited) {
                            heartIcon.className = 'fa-solid fa-heart heart-icon text-danger';
                        } else {
                            heartIcon.className = 'fa-regular fa-heart heart-icon';
                        }
                    }
                } else {
                    alert(data.message || '操作失敗，請稍後再試。');
                }
            } catch (error) {
                console.error('Error toggling favorite:', error);
                alert('發生錯誤，請重試！');
            }
        });
    }

    // ----------------- AJAX Submit Restaurant Review -----------------
    if (submitReviewBtn) {
        submitReviewBtn.addEventListener('click', async () => {
            const restaurantId = favoriteBtn?.dataset.restaurantId;
            if (!restaurantId) return;

            const ratingInput = document.querySelector('input[name="rating-stars"]:checked');
            const comment = reviewComment?.value || '';

            if (!ratingInput) {
                alert('請選取一個星級評分！');
                return;
            }

            const rating = ratingInput.value;

            try {
                const response = await fetch('/api/reviews/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        restaurant_id: restaurantId,
                        rating: rating,
                        comment: comment
                    })
                });

                if (response.status === 401) {
                    alert('請登入帳號後再發表評語！');
                    window.location.href = '/login';
                    return;
                }

                const data = await response.json();
                if (data.status === 'success') {
                    alert(data.message);
                    // Clear review fields
                    if (reviewComment) reviewComment.value = '';
                    const checkedRadio = document.querySelector('input[name="rating-stars"]:checked');
                    if (checkedRadio) checkedRadio.checked = false;
                    
                    // Dynamic updates
                    renderReviews(data.reviews);
                } else {
                    alert(data.message || '評論失敗，請稍後再試。');
                }
            } catch (error) {
                console.error('Error adding review:', error);
                alert('發生錯誤，請重試！');
            }
        });
    }

    // ----------------- Favorites Page Draw & Quick Remove -----------------
    const drawFavBtn = document.getElementById('draw-fav-btn');
    const favDrawResultContainer = document.getElementById('fav-draw-result-container');
    const closeFavDrawBtn = document.getElementById('close-fav-draw-btn');
    
    // Draw Favorite Results elements
    const favResImage = document.getElementById('fav-res-image');
    const favResName = document.getElementById('fav-res-name');
    const favResCategory = document.getElementById('fav-res-category');
    const favResRating = document.getElementById('fav-res-rating');
    const favResReviews = document.getElementById('fav-res-reviews');
    const favResAddress = document.getElementById('fav-res-address');
    const favResHours = document.getElementById('fav-res-hours');
    const favResMapsBtn = document.getElementById('fav-res-maps-btn');
    const favResHeartBtn = document.getElementById('fav-res-heart-btn');

    // New Upgraded elements for Favorites drawn popup
    const favResStatusBadge = document.getElementById('fav-res-status-badge');
    const favResDistanceBadge = document.getElementById('fav-res-distance-badge');
    const favResPriceGauge = document.getElementById('fav-res-price-gauge');
    const favResPriceText = document.getElementById('fav-res-price-text');
    const favResSignatureTags = document.getElementById('fav-res-signature-tags');
    const favResSignatureBox = document.getElementById('fav-res-signature-box');

    if (drawFavBtn) {
        drawFavBtn.addEventListener('click', async () => {
            const originalText = drawFavBtn.innerHTML;
            drawFavBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> 正在最愛中抽取...';
            drawFavBtn.classList.add('loading-pulse');
            drawFavBtn.disabled = true;

            try {
                // Slower delay for extreme surprise excitement
                await new Promise(r => setTimeout(r, 1000));
                
                const response = await fetch('/api/favorites/draw');
                const data = await response.json();

                if (data.status === 'success') {
                    const r = data.data;

                    if (favResName) favResName.textContent = r.name;
                    if (favResImage) favResImage.src = r.photo_url || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4';
                    if (favResCategory) favResCategory.textContent = r.category || '未分類';
                    if (favResRating) favResRating.textContent = r.rating || 'N/A';
                    if (favResReviews) favResReviews.textContent = r.user_ratings_total || '0';
                    if (favResAddress) favResAddress.textContent = r.address || '無地址';
                    if (favResHours) favResHours.textContent = r.open_hours || '未提供營業時間';
                    
                    if (favResPriceText) {
                        const p = r.price_level;
                        favResPriceText.textContent = p === 1 ? '平價餐點' : p === 2 ? '中等價位' : p === 3 ? '高檔享受' : '奢華饗宴';
                    }

                    // Render dynamic elements for fav drawn item
                    if (favResStatusBadge) {
                        const statusObj = parseBusinessStatus(r.open_hours);
                        favResStatusBadge.className = `badge rounded-pill px-3 py-2 fw-bold fs-7 shadow-sm ${statusObj.badgeClass}`;
                        favResStatusBadge.innerHTML = statusObj.text;
                    }

                    if (favResDistanceBadge) {
                        const distObj = calculateDistanceAndTravel(r.latitude, r.longitude);
                        favResDistanceBadge.innerHTML = `<i class="fa-solid fa-location-crosshairs text-danger me-1"></i> ${distObj.distanceText} <span class="mx-1 text-muted">|</span> ${distObj.travelHtml}`;
                    }

                    if (favResPriceGauge) {
                        favResPriceGauge.innerHTML = renderPriceGauge(r.price_level);
                    }

                    if (favResSignatureTags && favResSignatureBox) {
                        renderSignatureTags(r.signature, favResSignatureTags, favResSignatureBox);
                    }

                    if (favResHeartBtn) {
                        favResHeartBtn.dataset.restaurantId = r.id;
                    }

                    const encodedName = encodeURIComponent(r.name + ' ' + (r.address || ''));
                    if (favResMapsBtn) favResMapsBtn.href = `https://www.google.com/maps/search/?api=1&query=${encodedName}`;

                    // Show container
                    if (favDrawResultContainer) {
                        favDrawResultContainer.classList.remove('d-none');
                        favDrawResultContainer.classList.add('d-flex');
                        favDrawResultContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error('Error drawing favorite restaurant:', error);
                alert('抽取最愛失敗，請稍後重試！');
            } finally {
                drawFavBtn.innerHTML = originalText;
                drawFavBtn.classList.remove('loading-pulse');
                drawFavBtn.disabled = false;
            }
        });
    }

    if (closeFavDrawBtn) {
        closeFavDrawBtn.addEventListener('click', () => {
            if (favDrawResultContainer) {
                favDrawResultContainer.classList.add('d-none');
                favDrawResultContainer.classList.remove('d-flex');
            }
        });
    }

    if (favResHeartBtn) {
        favResHeartBtn.addEventListener('click', async () => {
            const restaurantId = favResHeartBtn.dataset.restaurantId;
            if (!restaurantId) return;

            if (confirm('確定要取消收藏這家精選餐廳嗎？')) {
                try {
                    const response = await fetch('/api/favorites/toggle', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ restaurant_id: restaurantId })
                    });
                    const data = await response.json();
                    if (data.status === 'success') {
                        // Close result card and fade card dynamically
                        if (favDrawResultContainer) {
                            favDrawResultContainer.classList.add('d-none');
                            favDrawResultContainer.classList.remove('d-flex');
                        }
                        
                        const cardCol = document.getElementById(`fav-card-${restaurantId}`);
                        if (cardCol) {
                            cardCol.classList.add('fade-out');
                            setTimeout(() => {
                                cardCol.remove();
                                const remaining = document.querySelectorAll('.favorite-card-col');
                                if (remaining.length === 0) {
                                    location.reload();
                                }
                            }, 400);
                        }
                    }
                } catch (error) {
                    console.error('Error unfavoriting drawn item:', error);
                }
            }
        });
    }

    // Cancel Favorites Button AJAX Clicker
    const cancelFavButtons = document.querySelectorAll('.cancel-fav-btn');
    cancelFavButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const restaurantId = btn.dataset.restaurantId;
            if (!restaurantId) return;

            if (confirm('確定要將這家餐廳從您的收藏中移除嗎？')) {
                try {
                    const response = await fetch('/api/favorites/toggle', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ restaurant_id: restaurantId })
                    });
                    const data = await response.json();

                    if (data.status === 'success') {
                        const cardCol = document.getElementById(`fav-card-${restaurantId}`);
                        if (cardCol) {
                            cardCol.classList.add('fade-out');
                            setTimeout(() => {
                                cardCol.remove();
                                const remaining = document.querySelectorAll('.favorite-card-col');
                                if (remaining.length === 0) {
                                    location.reload();
                                }
                            }, 400);
                        }
                    } else {
                        alert(data.message || '取消收藏失敗，請稍後重試！');
                    }
                } catch (error) {
                    console.error('Error cancelling favorite:', error);
                    alert('發生錯誤，請重試！');
                }
            }
        });
    });

    // ----------------- Reviews Page AJAX Deletion -----------------
    const deleteReviewButtons = document.querySelectorAll('.delete-my-review-btn');
    deleteReviewButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const reviewId = btn.dataset.reviewId;
            if (!reviewId) return;

            if (confirm('您確定要永久刪除這筆餐廳評價紀錄嗎？')) {
                try {
                    const response = await fetch(`/api/reviews/delete/${reviewId}`, {
                        method: 'POST'
                    });
                    const data = await response.json();

                    if (data.status === 'success') {
                        const reviewItem = document.getElementById(`review-item-${reviewId}`);
                        if (reviewItem) {
                            reviewItem.classList.add('fade-out');
                            setTimeout(() => {
                                reviewItem.remove();
                                const remaining = document.querySelectorAll('.review-card-item');
                                if (remaining.length === 0) {
                                    location.reload();
                                }
                            }, 400);
                        }
                    } else {
                        alert(data.message || '刪除評價失敗，請稍後重試！');
                    }
                } catch (error) {
                    console.error('Error deleting review:', error);
                    alert('發生錯誤，請重試！');
                }
            }
        });
    });
});
