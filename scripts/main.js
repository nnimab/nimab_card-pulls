// 卡牌數據
const CARDS_CONFIG = {
    yijing: {
        total: 64,
        name: '易經卦卡',
        symbol: '★',
        color: '#00ffff',
        gradient: 'linear-gradient(45deg, #2c3e50, #3498db)'
    },
    spacetime: {
        total: 22,
        name: '時空卡',
        symbol: '○',
        color: '#ff6b6b',
        gradient: 'linear-gradient(45deg, #4b134f, #c94b4b)'
    },
    character: {
        total: 22,
        name: '人物卡',
        symbol: '☺',
        color: '#4cd137',
        gradient: 'linear-gradient(45deg, #134e5e, #71b280)'
    }
};

// 初始化各類型卡片數組
let cardDecks = {
    yijing: Array.from({ length: CARDS_CONFIG.yijing.total }, (_, i) => i + 1),
    spacetime: Array.from({ length: CARDS_CONFIG.spacetime.total }, (_, i) => i + 1),
    character: Array.from({ length: CARDS_CONFIG.character.total }, (_, i) => i + 1)
};

// 當前選擇的卡片類型
let currentCardType = 'yijing';

// 卡片描述緩存
const cardDescriptions = {
    yijing: {},
    spacetime: {},
    character: {}
};

// 易經卦卡資料緩存
const yijingCardData = {};

// 加載易經卦卡資料
async function loadYijingCardData() {
    try {
        // 使用JSON文件而不是Excel文件
        const response = await fetch('易經卡基本資料.json');
        if (!response.ok) {
            throw new Error('無法載入易經卦卡資料');
        }
        
        // 解析JSON數據
        const cardDataArray = await response.json();
        
        // 處理每一條卡片數據
        cardDataArray.forEach(card => {
            // 從卦名中提取卦號
            const match = card.卦名.match(/(\d+)/);
            if (match) {
                const cardNumber = parseInt(match[1]);
                
                // 存儲卡片數據
                yijingCardData[cardNumber] = {
                    number: match[1],
                    name: card.卦名,
                    attribute: card.屬性,
                    yinYang: card.陰陽,
                    words: card.卦詞
                };
            }
        });
        
        console.log('成功載入易經卦卡資料:', Object.keys(yijingCardData).length, '張卡片');
    } catch (error) {
        console.error('載入易經卦卡資料時出錯：', error);
    }
}

// 獲取卡片圖片路徑
function getCardImagePath(cardNumber) {
    // 簡化的路徑處理，假設所有資料夾都是純數字，所有圖片都命名為01.png
    return [`images/yijing/${cardNumber}/01.png`];
}

// 加載卡片描述
async function loadCardDescription(cardNumber, cardType) {
    // 如果已經在緩存中，直接返回
    if (cardDescriptions[cardType][cardNumber]) {
        return cardDescriptions[cardType][cardNumber];
    }

    try {
        // 讀取對應的 Markdown 文件
        const response = await fetch(`card-descriptions/${cardType}/${cardNumber}.md`);
        if (!response.ok) {
            throw new Error(`找不到卡片 ${cardNumber} 的描述文件`);
        }
        const text = await response.text();
        
        // 將描述存入緩存
        cardDescriptions[cardType][cardNumber] = text;
        return text;
    } catch (error) {
        console.warn(`無法載入卡片 ${cardNumber} 的描述：`, error);
        return `${CARDS_CONFIG[cardType].name} ${cardNumber} 的描述文本尚未添加。`;
    }
}

// 音效控制
let soundEnabled = true;
let audioContext = null;

// DOM 元素
const fanCardsContainer = document.getElementById('fanCards');
const toggleSoundBtn = document.getElementById('toggleSound');
const confirmDialog = document.querySelector('.confirm-dialog');
const overlay = document.querySelector('.overlay');
const confirmBtn = document.querySelector('.confirm-btn');
const cancelBtn = document.querySelector('.cancel-btn');
const clearBtn = document.querySelector('.clear-btn');
const cardDetailView = document.createElement('div');
cardDetailView.className = 'card-detail-view';
document.body.appendChild(cardDetailView);

let selectedCard = null;

// 顯示確認框
function showConfirmDialog() {
    confirmDialog.classList.add('active');
    overlay.classList.add('active');
    fanCardsContainer.classList.add('confirming');
    
    // 確保確認和取消按鈕可以接收點擊事件
    confirmBtn.style.pointerEvents = 'auto';
    cancelBtn.style.pointerEvents = 'auto';
    
    // 將確認對話框移到 body 的最後，確保它不受其他元素的影響
    document.body.appendChild(confirmDialog);
}

// 隱藏確認框
function hideConfirmDialog() {
    confirmDialog.classList.remove('active');
    overlay.classList.remove('active');
    fanCardsContainer.classList.remove('confirming');
    if (selectedCard) {
        selectedCard.classList.remove('selected');
        selectedCard = null;
    }
    
    // 將確認對話框放回原位
    fanCardsContainer.appendChild(confirmDialog);
}

// 計算扇形分布
function calculateSpread() {
    const container = fanCardsContainer.getBoundingClientRect();
    const containerHeight = container.height;
    const containerWidth = container.width;
    const factor = window.innerWidth <= 768 ? 0.3 : 0.35;
    const radius = -Math.min(containerHeight * factor, containerWidth * factor);
    return {
        radius: radius,
        containerHeight: containerHeight,
        containerWidth: containerWidth
    };
}

// 創建音效
function createCardSound() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.05);
    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.3);
    
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.3);
}

// 修改處理卡牌抽取函數
function handleCardDraw(event) {
    const card = event.target;
    if (card.classList.contains('drawing')) return;

    // 播放音效
    if (soundEnabled) {
        createCardSound();
    }

    // 添加抽取動畫
    card.classList.add('drawing');

    const currentDeck = cardDecks[currentCardType];
    if (currentDeck.length === 0) {
        alert(`${CARDS_CONFIG[currentCardType].name}已經抽完了！`);
        card.classList.remove('drawing');
        return;
    }

    // 隨機選擇一張卡牌
    const randomIndex = Math.floor(Math.random() * currentDeck.length);
    const drawnCard = currentDeck[randomIndex];
    currentDeck.splice(randomIndex, 1);

    // 找到對應類型的第一個空卡槽
    const emptySlot = document.querySelector(`.${currentCardType}-slots .card-slot:empty`);
    if (emptySlot) {
        setTimeout(() => {
            const displayCard = document.createElement('div');
            displayCard.className = 'card drawn';
            displayCard.dataset.cardType = currentCardType;
            displayCard.dataset.cardNumber = drawnCard; // 保存卡片編號
            displayCard.dataset.originalType = currentCardType; // 保存原始卡片類型
            
            // 如果是易經卦卡，使用圖片和更多信息
            if (currentCardType === 'yijing') {
                const cardData = yijingCardData[drawnCard] || {
                    number: drawnCard,
                    name: `卦象${drawnCard}`,
                    attribute: '未知',
                    yinYang: '未知'
                };
                
                // 根據陰陽屬性設置顏色
                const yinYangColor = cardData.yinYang === '陰' ? '#3498db' : '#f1c40f';
                
                // 設置五行屬性對應的顏色
                let attributeColors = [];
                cardData.attribute.split('').forEach(attr => {
                    // 根據五行屬性設置不同顏色
                    switch(attr) {
                        case '金':
                            attributeColors.push('#FFFFFF'); // 金為白色
                            break;
                        case '木':
                            attributeColors.push('#4CAF50'); // 綠色
                            break;
                        case '水':
                            attributeColors.push('#607D8B'); // 灰色
                            break;
                        case '火':
                            attributeColors.push('#FF5722'); // 火紅色
                            break;
                        case '土':
                            attributeColors.push('#8B4513'); // 土褐色
                            break;
                        default:
                            attributeColors.push('#ffffff'); // 默認白色
                    }
                });
                
                // 獲取卡片圖片路徑
                const imagePaths = getCardImagePath(drawnCard);
                
                displayCard.innerHTML = `
                    <div class="drawn-card-content">
                        <div class="drawn-card-header">
                            <div class="drawn-card-name">${cardData.name}</div>
                            <div class="drawn-card-attribute">
                                <span style="color: ${yinYangColor};">${cardData.yinYang}</span> | 
                                <span style="color: ${attributeColors[0] || '#ffffff'};">${cardData.attribute.charAt(0) || ''}</span>
                                <span style="color: ${attributeColors[1] || '#ffffff'};">${cardData.attribute.charAt(1) || ''}</span>
                            </div>
                        </div>
                        <div class="drawn-card-image">
                            <img src="${imagePaths[0]}" alt="${cardData.name}" onerror="if (this.getAttribute('data-tried') === null) { this.setAttribute('data-tried', '0'); } let tried = parseInt(this.getAttribute('data-tried')); if (tried < ${imagePaths.length - 1}) { this.setAttribute('data-tried', tried + 1); this.src='${imagePaths[1] || ''}'; } else if (tried === ${imagePaths.length - 1}) { this.onerror = null; this.src='images/yijing/1/0_1.png'; }">
                        </div>
                    </div>
                `;
            } else {
                // 其他類型卡片使用原來的顯示方式
                displayCard.textContent = drawnCard;
            }
            
            displayCard.style.background = CARDS_CONFIG[currentCardType].gradient;
            displayCard.style.borderColor = CARDS_CONFIG[currentCardType].color;
            
            // 添加點擊事件來顯示詳細視圖
            displayCard.addEventListener('click', () => {
                // 使用保存的原始類型來顯示描述
                const cardType = displayCard.dataset.originalType;
                const cardNumber = displayCard.dataset.cardNumber;
                createDetailView(cardNumber, cardType).catch(error => {
                    console.error('顯示卡片詳細信息時出錯：', error);
                });
            });
            
            emptySlot.appendChild(displayCard);
            card.remove();
            updateClearButtonState();
        }, 500);
    } else {
        alert(`${CARDS_CONFIG[currentCardType].name}的放置區已滿！`);
        card.classList.remove('drawing');
        currentDeck.push(drawnCard); // 將卡片放回牌組
    }
}

// 修改創建詳細視圖內容函數
async function createDetailView(cardNumber, cardType) {
    cardDetailView.dataset.cardType = cardType; // 設置卡片類型
    // 載入卡片描述
    const description = await loadCardDescription(cardNumber, cardType);

    // 將 Markdown 轉換為 HTML
    const htmlContent = marked.parse(description);

    let cardContent = '';
    
    // 如果是易經卦卡，使用完整的卡片顯示
    if (cardType === 'yijing') {
        // 獲取卡片數據
        const cardData = yijingCardData[cardNumber] || {
            number: cardNumber,
            name: `卦象${cardNumber}`,
            attribute: '未知',
            yinYang: '未知',
            words: '無卦詞'
        };
        
        // 根據陰陽屬性設置顏色
        const yinYangColor = cardData.yinYang === '陰' ? '#3498db' : '#f1c40f';
        
        // 設置五行屬性對應的顏色
        let attributeColors = [];
        cardData.attribute.split('').forEach(attr => {
            // 根據五行屬性設置不同顏色
            switch(attr) {
                case '金':
                    attributeColors.push('#FFFFFF'); // 金為白色
                    break;
                case '木':
                    attributeColors.push('#4CAF50'); // 綠色
                    break;
                case '水':
                    attributeColors.push('#607D8B'); // 灰色
                    break;
                case '火':
                    attributeColors.push('#FF5722'); // 火紅色
                    break;
                case '土':
                    attributeColors.push('#8B4513'); // 土褐色
                    break;
                default:
                    attributeColors.push('#ffffff'); // 默認白色
            }
        });
        
        // 獲取卡片圖片路徑
        const imagePaths = getCardImagePath(cardNumber);
        
        // 創建完整卡片視圖，類似於您提供的圖片
        cardContent = `
            <div class="full-card-view">
                <div class="full-card-header">
                    <div class="full-card-number">${cardNumber} ${cardData.name.replace(/^\d+\s*/, '')}</div>
                    <div class="full-card-attribute">
                        <span style="color: ${yinYangColor};">${cardData.yinYang}</span> | 
                        <span style="color: ${attributeColors[0] || '#ffffff'};">${cardData.attribute.charAt(0) || ''}</span>
                        <span style="color: ${attributeColors[1] || '#ffffff'};">${cardData.attribute.charAt(1) || ''}</span>
                    </div>
                </div>
                <div class="full-card-image">
                    <img src="${imagePaths[0]}" alt="${cardData.name}" style="max-height: 100%; max-width: 100%;" onerror="if (this.getAttribute('data-tried') === null) { this.setAttribute('data-tried', '0'); } let tried = parseInt(this.getAttribute('data-tried')); if (tried < ${imagePaths.length - 1}) { this.setAttribute('data-tried', tried + 1); this.src='${imagePaths[1] || ''}'; } else if (tried === ${imagePaths.length - 1}) { this.onerror = null; this.src='images/yijing/1/0_1.png'; }">
                </div>
                <div class="full-card-words">${cardData.words}</div>
            </div>
            <div class="scroll-hint" style="color: ${CARDS_CONFIG[cardType].color}">下滑查看更多資訊</div>
            <div class="card-detail-text" id="cardDescription" style="--accent-color: ${CARDS_CONFIG[cardType].color}">${htmlContent}</div>
        `;
    } else {
        // 其他類型卡片使用原來的顯示方式
        cardContent = `
            <div class="card-detail-image" data-card-type="${cardType}" style="background: ${CARDS_CONFIG[cardType].gradient}; border-color: ${CARDS_CONFIG[cardType].color}; box-shadow: 0 0 30px ${CARDS_CONFIG[cardType].color};">
                <div class="inner-content">${cardNumber}</div>
            </div>
            <div class="scroll-hint" style="color: ${CARDS_CONFIG[cardType].color}">下滑查看更多資訊</div>
            <div class="card-detail-text" id="cardDescription" style="--accent-color: ${CARDS_CONFIG[cardType].color}">${htmlContent}</div>
        `;
    }

    const content = `
        <button class="close-detail-btn" style="color: ${CARDS_CONFIG[cardType].color}">&times;</button>
        <div class="card-detail-content">
            ${cardContent}
        </div>
    `;
    cardDetailView.innerHTML = content;

    // 添加關閉按鈕事件
    const closeBtn = cardDetailView.querySelector('.close-detail-btn');
    closeBtn.addEventListener('click', () => {
        cardDetailView.classList.remove('active');
    });
    
    closeBtn.addEventListener('mouseover', () => {
        closeBtn.style.color = CARDS_CONFIG[cardType].color;
    });

    // 添加滾動提示點擊事件
    const scrollHint = cardDetailView.querySelector('.scroll-hint');
    const cardDescription = cardDetailView.querySelector('#cardDescription');
    
    if (scrollHint && cardDescription) {
        scrollHint.addEventListener('click', () => {
            cardDescription.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        });

        // 監聽滾動事件來控制提示的顯示
        cardDetailView.addEventListener('scroll', () => {
            const scrollPosition = cardDetailView.scrollTop;
            if (scrollPosition > 100) {
                scrollHint.style.opacity = '0';
                scrollHint.style.pointerEvents = 'none';
            } else {
                scrollHint.style.opacity = '0.8';
                scrollHint.style.pointerEvents = 'auto';
            }
        });
    }

    // 修改 Markdown 樣式中的顏色
    const markdownElements = cardDetailView.querySelectorAll('.card-detail-text h1, .card-detail-text h2, .card-detail-text strong');
    markdownElements.forEach(element => {
        element.style.color = CARDS_CONFIG[cardType].color;
    });

    if (cardDetailView.querySelector('.card-detail-text h1')) {
        cardDetailView.querySelector('.card-detail-text h1').style.borderBottomColor = CARDS_CONFIG[cardType].color;
    }

    cardDetailView.classList.add('active');
}

// 添加確認和取消按鈕的事件監聽器
confirmBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // 防止事件冒泡
    e.preventDefault(); // 防止默認行為
    console.log('確認按鈕被點擊');
    if (selectedCard) {
        handleCardDraw({ target: selectedCard });
        hideConfirmDialog();
    }
});

cancelBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // 防止事件冒泡
    e.preventDefault(); // 防止默認行為
    console.log('取消按鈕被點擊');
    hideConfirmDialog();
});

// 防止確認框的點擊事件冒泡
confirmDialog.addEventListener('click', (e) => {
    e.stopPropagation();
});

// 音效開關控制
toggleSoundBtn.addEventListener('click', () => {
    soundEnabled = !soundEnabled;
    toggleSoundBtn.querySelector('.sound-on').style.display = 
        soundEnabled ? 'inline' : 'none';
    toggleSoundBtn.querySelector('.sound-off').style.display = 
        soundEnabled ? 'none' : 'inline';
});

// 處理視窗大小變化
window.addEventListener('resize', () => {
    const spread = calculateSpread();
    const cards = document.querySelectorAll('.card');
    let totalAngle = window.innerWidth <= 768 ? 60 : 100;
    const startAngle = -totalAngle / 2;
    const angleStep = totalAngle / (CARDS_CONFIG[currentCardType].total - 1);
    cards.forEach((card, index) => {
        const rotation = startAngle + (angleStep * index);
        card.style.setProperty('--rotation', `${rotation}deg`);
        card.style.setProperty('--radius', spread.radius);
    });
});

// 修改清除功能
function clearCards() {
    const drawnCards = document.querySelectorAll('.card.drawn');
    if (drawnCards.length === 0) return;

    // 播放音效
    if (soundEnabled) {
        createCardSound();
    }

    // 將卡片放回對應的牌組
    drawnCards.forEach(card => {
        const cardType = card.dataset.cardType;
        const cardNumber = parseInt(card.textContent);
        cardDecks[cardType].push(cardNumber);
        card.remove();
    });

    // 重新初始化扇形
    const cardElements = fanCardsContainer.querySelectorAll('.card');
    cardElements.forEach(card => card.remove());
    initializeFanCards();

    // 更新按鈕狀態
    updateClearButtonState();
}

// 更新清除按鈕狀態
function updateClearButtonState() {
    const drawnCards = document.querySelectorAll('.card.drawn');
    clearBtn.disabled = drawnCards.length === 0;
}

// 添加清除按鈕事件監聽器
clearBtn.addEventListener('click', clearCards);

// 添加點擊背景關閉詳細視圖的功能
cardDetailView.addEventListener('click', (e) => {
    if (e.target === cardDetailView) {
        cardDetailView.classList.remove('active');
    }
});

// 修改初始化卡片類型選擇器
function initializeCardTypeSelector() {
    const typeButtons = document.querySelectorAll('.type-btn');
    typeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 移除其他按鈕的活動狀態
            typeButtons.forEach(b => b.classList.remove('active'));
            // 添加當前按鈕的活動狀態
            btn.classList.add('active');
            // 更新當前卡片類型
            currentCardType = btn.dataset.type;
            // 重新初始化扇形（但不清除已抽出的卡片）
            const cardElements = fanCardsContainer.querySelectorAll('.card');
            cardElements.forEach(card => card.remove());
            initializeFanCards();
        });
    });
    
    // 設置預設選中狀態
    const defaultButton = document.querySelector('.type-btn[data-type="yijing"]');
    if (defaultButton) {
        defaultButton.classList.add('active');
    }
}

// 修改初始化扇形卡牌
function initializeFanCards() {
    const spread = calculateSpread();
    const totalCards = CARDS_CONFIG[currentCardType].total;
    let totalAngle = window.innerWidth <= 768 ? 60 : 100;
    const startAngle = -totalAngle / 2;
    const angleStep = totalAngle / (totalCards - 1);

    for (let i = 0; i < totalCards; i++) {
        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.index = i;
        card.dataset.cardType = currentCardType;
        
        const rotation = startAngle + (angleStep * i);
        card.style.setProperty('--rotation', `${rotation}deg`);
        card.style.setProperty('--radius', spread.radius);
        card.style.setProperty('--symbol', `'${CARDS_CONFIG[currentCardType].symbol}'`);
        card.style.background = CARDS_CONFIG[currentCardType].gradient;
        
        // 不在背面顯示資訊，保持原有的星星形狀
        
        // 添加點擊事件
        card.addEventListener('click', (e) => {
            if (confirmDialog.classList.contains('active')) return;
            
            selectedCard = e.target.closest('.card');
            if (!selectedCard) return;
            
            selectedCard.classList.add('selected');
            showConfirmDialog();
        });
        
        fanCardsContainer.appendChild(card);
    }
}

// 記錄最後一次點擊時間（用於檢測雙擊）
let lastTapTime = 0;

// 檢查是否需要顯示滾動提示
function checkScrollIndicator() {
    const container = document.querySelector('.card-slots-container');
    const indicator = document.querySelector('.scroll-indicator');
    
    if (!container || !indicator) return;
    
    // 如果內容高度大於容器高度，顯示滾動提示，否則隱藏
    if (container.scrollHeight > container.clientHeight) {
        indicator.style.display = 'block';
    } else {
        indicator.style.display = 'none';
    }
}

// 在初始化和窗口大小改變時檢查滾動提示
window.addEventListener('load', checkScrollIndicator);
window.addEventListener('resize', checkScrollIndicator);

// 點擊滾動提示箭頭時，向下滾動一點
document.querySelector('.scroll-indicator')?.addEventListener('click', function() {
    const container = document.querySelector('.card-slots-container');
    if (container) {
        container.scrollBy({
            top: 100,
            behavior: 'smooth'
        });
    }
});

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 載入易經卦卡資料
    await loadYijingCardData();
    
    // 初始化卡片類型選擇器
    initializeCardTypeSelector();
    
    // 初始化扇形卡牌
    initializeFanCards();
    
    // 初始化清除按鈕狀態
    updateClearButtonState();
    
    // 設置音效按鈕初始狀態
    toggleSoundBtn.querySelector('.sound-on').style.display = 'inline';
    toggleSoundBtn.querySelector('.sound-off').style.display = 'none';
}); 