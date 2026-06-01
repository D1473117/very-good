document.addEventListener('DOMContentLoaded', function() {
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const locationBadge = document.getElementById('locationBadge');
    const locationText = document.getElementById('locationText');
    const spinBtn = document.getElementById('spinBtn');
    const shuffleText = document.getElementById('shuffleText');
    const shuffleCategory = document.getElementById('shuffleCategory');
    
    // Default coords: Feng Chia University
    const DEFAULT_LAT = 24.1786;
    const DEFAULT_LNG = 120.6468;

    // 1. Get Geolocation on page load
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // Success callback
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                latInput.value = lat;
                lngInput.value = lng;
                
                // Update location status badge
                locationBadge.className = "badge rounded-pill bg-success-translucent py-2 px-3 text-white border-success-glow";
                locationBadge.innerHTML = `<i class="bi bi-geo-fill text-success-bright me-2"></i>已取得您的 GPS 定位`;
                console.log(`GPS Location obtained: ${lat}, ${lng}`);
            },
            function(error) {
                // Error callback (permission denied, timeout, etc.)
                console.warn(`Geolocation error (${error.code}): ${error.message}. Using Feng Chia University as default.`);
                fallbackToDefaultLocation("定位遭拒/失敗，預設逢甲大學");
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    } else {
        console.warn("Browser does not support Geolocation. Using Feng Chia University as default.");
        fallbackToDefaultLocation("瀏覽器不支援定位，預設逢甲大學");
    }

    function fallbackToDefaultLocation(msg) {
        latInput.value = DEFAULT_LAT;
        lngInput.value = DEFAULT_LNG;
        locationBadge.className = "badge rounded-pill bg-warning-translucent py-2 px-3 text-white border-warning-glow";
        locationBadge.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-warning-bright me-2"></i>${msg}`;
    }

    // List of food terms to display during the shuffling animation
    const shuffleFoodList = [
        "正在過濾料理類別...",
        "正在計算商家距離...",
        "正在比對預算價位...",
        "正在剔除評分較低商家...",
        "日式拉麵？",
        "香噴噴的香酥雞排？",
        "熱騰騰的麻辣小火鍋？",
        "大腸包小腸？",
        "來杯熟成紅茶？",
        "香濃的義大利麵？",
        "韓式辣炒年糕？",
        "清爽無負擔的蔬食？",
        "手作冰品甜點？",
        "正在抽出您的天選美食...",
        "美味即將揭曉...",
        "不要眨眼，骰子轉動中..."
    ];

    // 2. Intercept Spin Button
    spinBtn.addEventListener('click', function() {
        const category = document.getElementById('category').value;
        const price_range = document.getElementById('price_range').value;
        const distance = document.getElementById('distance').value;
        const latitude = latInput.value;
        const longitude = lngInput.value;

        // Disable UI
        spinBtn.disabled = true;
        spinBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>正在抽選中...`;
        
        // Start Shuffling Text Animation
        let shuffleIndex = 0;
        const shuffleInterval = setInterval(function() {
            shuffleText.innerText = shuffleFoodList[shuffleIndex % shuffleFoodList.length];
            shuffleCategory.innerText = "🎲 隨機滾動中 🎲";
            shuffleIndex++;
        }, 100);

        const startTime = Date.now();

        // Send AJAX Post Request
        fetch('/spin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category: category,
                price_range: price_range,
                distance: distance,
                latitude: latitude,
                longitude: longitude
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || "找不到符合條件的餐廳") });
            }
            return response.json();
        })
        .then(data => {
            // Guarantee at least 1.5 seconds of animation for aesthetic wow effect
            const elapsedTime = Date.now() - startTime;
            const remainingTime = Math.max(0, 1500 - elapsedTime);

            setTimeout(function() {
                clearInterval(shuffleInterval);
                
                // Show result in the shuffle container briefly
                const res = data.restaurant;
                shuffleText.innerText = res.name;
                shuffleCategory.innerText = `🎉 抽中：${res.category} | 評價：★${res.rating}`;
                
                // Populate Modal Elements
                document.getElementById('resName').innerText = res.name;
                document.getElementById('resCategory').innerText = res.category;
                document.getElementById('resPrice').innerText = res.price_range;
                document.getElementById('resRating').innerText = `${res.rating} 分`;
                document.getElementById('resAddress').innerText = res.address;
                document.getElementById('resPhone').innerText = res.phone;
                document.getElementById('resHours').innerText = res.operating_hours;
                
                // Set Distance Badge
                const distBadge = document.getElementById('resDistance');
                if (res.distance !== null && res.distance !== undefined) {
                    distBadge.innerText = `距離約 ${res.distance} 公尺`;
                    distBadge.classList.remove('d-none');
                } else {
                    distBadge.classList.add('d-none');
                }

                // Render Stars
                const starsContainer = document.getElementById('resStars');
                starsContainer.innerHTML = '';
                const starsCount = Math.round(res.rating);
                for (let i = 1; i <= 5; i++) {
                    const starIcon = document.createElement('i');
                    if (i <= starsCount) {
                        starIcon.className = 'bi bi-star-fill text-warning me-1';
                    } else {
                        starIcon.className = 'bi bi-star text-white-50 me-1';
                    }
                    starsContainer.appendChild(starIcon);
                }

                // Set Google Maps Map Embed URL
                const mapIframe = document.getElementById('resMap');
                if (res.google_maps_url) {
                    mapIframe.src = res.google_maps_url;
                } else {
                    mapIframe.src = `https://maps.google.com/maps?q=${res.name}&hl=zh-TW&z=15&output=embed`;
                }

                // Set Detail Page Link
                document.getElementById('resDetailLink').href = `/restaurant/${res.id}`;

                // Set Favorite Form Values
                document.getElementById('favName').value = res.name;
                document.getElementById('favCategory').value = res.category;
                document.getElementById('favRating').value = res.rating;
                document.getElementById('favAddress').value = res.address;

                // Show Modal
                const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
                resultModal.show();

                // Re-enable UI
                spinBtn.disabled = false;
                spinBtn.innerHTML = `<i class="bi bi-dice-5-fill me-2 fs-3"></i>骰出幸運餐廳！`;
            }, remainingTime);
        })
        .catch(error => {
            clearInterval(shuffleInterval);
            spinBtn.disabled = false;
            spinBtn.innerHTML = `<i class="bi bi-dice-5-fill me-2 fs-3"></i>骰出幸運餐廳！`;
            
            shuffleText.innerText = "今天的幸運餐廳是...？";
            shuffleCategory.innerText = "點擊下方按鈕開始抽選";
            
            alert(`⚠️ 抽選出錯：${error.message}`);
        });
    });
});
