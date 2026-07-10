// ========================================================
// 组员4（攻略+社区）专用前端联调脚本
// ========================================================

async function loadCommunityGuides() {
    try {
        const response = await fetch('/api/guides/');
        const result = await response.json();
        if (result.status === 'success') {
            const container = document.getElementById('guide-list-container') || document.getElementById('testemonial-carousel');
            if (!container) return;
            
            // 如果原本已经有了 Owl 轮播图实例，先销毁它以便重新加载数据
            const $carousel = jQuery(container);
            if ($carousel.data('owl.carousel')) {
                $carousel.owlCarousel('destroy');
            }

            if (result.data.length === 0) {
                container.innerHTML = '<div class="text-center" style="width:100%; padding:20px;">暂无新攻略发布，快去发布第一篇吧！</div>';
                return;
            }

            // 完美的动态卡片注入，完全继承了同学 B 本来写好的漂亮样式！
            container.innerHTML = result.data.map(g => `
                <div class="home1-testm item">
                    <div class="home1-testm-single text-center">
                        <div class="home1-testm-txt">
                            <span class="icon section-icon">
                                <i class="fa fa-quote-left" aria-hidden="true"></i>
                            </span>
                            <h2 style="font-size: 18px; margin-bottom: 10px; color:#007BFF;">${g.title}</h2>
                            <p>${g.content || '暂无详细介绍'}</p>
                            <h3>
                                <a href="#">作者：${g.author}</a>
                            </h3>
                            <h4>目的地：${g.destination} | 发布于：${g.created_at}</h4>
                            <div style="margin-top: 15px;">
                                <button onclick="likeGuideAction(${g.id}, this)" style="background:#007BFF; color:white; border:none; padding:5px 15px; border-radius:20px; cursor:pointer;">
                                    👍 点赞 (<span class="like-count">${g.likes}</span>)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            // 数据渲染完毕后，重新激活轮播图动画特效
            if (jQuery.fn.owlCarousel) {
                jQuery(container).owlCarousel({
                    items: 2,
                    loop: result.data.length > 1,
                    margin: 30,
                    autoplay: true,
                    smartSpeed: 1000,
                    responsive: {
                        0: { items: 1 },
                        768: { items: 2 }
                    }
                });
            }
        }
    } catch (error) {
        console.error("加载攻略失败:", error);
    }
}

// 点赞点击事件
async function likeGuideAction(guideId, buttonElement) {
    try {
        const response = await fetch(`/api/guides/${guideId}/like/`, { method: 'POST' });
        const result = await response.json();
        if (result.status === 'success') {
            buttonElement.querySelector('.like-count').innerText = result.likes;
        }
    } catch (error) {
        console.error("点赞失败", error);
    }
}

// 页面加载完成后自动加载
document.addEventListener('DOMContentLoaded', () => {
    loadCommunityGuides();
});
