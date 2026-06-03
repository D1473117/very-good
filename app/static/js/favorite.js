document.addEventListener('DOMContentLoaded', function() {
    // 註冊所有的收藏按鈕點擊事件
    setupFavoriteButtons();
});

/**
 * 初始化頁面上的所有收藏按鈕
 */
function setupFavoriteButtons() {
    const favButtons = document.querySelectorAll('.favorite-btn-toggle, .card-fav-btn');
    
    favButtons.forEach(button => {
        // 防止重複綁定
        if (button.dataset.listenerAttached) return;
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const restaurantId = this.dataset.restaurantId;
            if (!restaurantId) return;
            
            toggleFavorite(restaurantId, this);
        });
        
        button.dataset.listenerAttached = 'true';
    });
}

/**
 * 透過 AJAX (Fetch API) 與後端切換收藏狀態
 * @param {string|number} restaurantId 餐廳 ID
 * @param {HTMLElement} buttonElement 點擊的按鈕元素
 */
function toggleFavorite(restaurantId, buttonElement) {
    // 停用按鈕，避免重複點擊
    buttonElement.style.pointerEvents = 'none';
    
    fetch('/favorite/toggle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            restaurant_id: restaurantId
        })
    })
    .then(response => {
        if (response.status === 401) {
            // 未登入，顯示提示或重導向
            showToast('請先登入後再進行此操作！', 'error');
            setTimeout(() => {
                window.location.href = '/auth/login';
            }, 1500);
            throw new Error('Unauthorized');
        }
        
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || '網路請求失敗');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const isFav = data.favorited;
            
            // 更新 UI 狀態
            updateButtonState(buttonElement, isFav);
            
            // 顯示成功 Toast
            if (isFav) {
                showToast('已成功加入收藏清單！ ❤️', 'success');
            } else {
                showToast('已從收藏清單中移除。 🤍', 'info');
                
                // 如果在我的收藏頁面，則在取消收藏後自動淡出卡片
                const card = buttonElement.closest('.restaurant-card');
                if (card && window.location.pathname.includes('/profile/favorites')) {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.9)';
                    setTimeout(() => {
                        card.remove();
                        // 檢查是否還有收藏
                        const container = document.querySelector('.grid');
                        if (container && container.children.length === 0) {
                            location.reload(); // 重整以顯示 empty state
                        }
                    }, 500);
                }
            }
        } else {
            showToast('操作失敗，請稍後再試！', 'error');
        }
    })
    .catch(error => {
        if (error.message !== 'Unauthorized') {
            console.error('Error toggling favorite:', error);
            showToast(error.message || '系統發生錯誤！', 'error');
        }
    })
    .finally(() => {
        // 恢復按鈕可點擊狀態
        buttonElement.style.pointerEvents = 'auto';
    });
}

/**
 * 根據收藏狀態更新按鈕樣式
 * @param {HTMLElement} buttonElement 按鈕元素
 * @param {boolean} isFav 是否被收藏
 */
function updateButtonState(buttonElement, isFav) {
    if (isFav) {
        buttonElement.classList.add('active');
        
        // 更換內部的圖示 (如果有 icon)
        const icon = buttonElement.querySelector('i');
        if (icon) {
            icon.className = 'bi bi-heart-fill';
        }
    } else {
        buttonElement.classList.remove('active');
        
        const icon = buttonElement.querySelector('i');
        if (icon) {
            icon.className = 'bi bi-heart';
        }
    }
}

/**
 * 顯示自訂的 Glassmorphic Toast 提示
 * @param {string} message 提示訊息
 * @param {string} type 樣式類型 ('success', 'error', 'info')
 */
function showToast(message, type = 'success') {
    // 建立 toast 容器 (若不存在)
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    // 建立單個 toast
    const toast = document.createElement('div');
    toast.className = `custom-toast toast-${type}`;
    
    let iconClass = 'bi-info-circle';
    if (type === 'success') iconClass = 'bi-check-circle-fill';
    if (type === 'error') iconClass = 'bi-exclamation-triangle-fill';
    
    toast.innerHTML = `
        <i class="bi ${iconClass}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // 定時淡出並移除
    setTimeout(() => {
        toast.classList.add('toast-hide');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// 暴露 showToast 給外部 (例如首頁的 spin 腳本)
window.showToast = showToast;
window.setupFavoriteButtons = setupFavoriteButtons;
