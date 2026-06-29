// 萌宠洗护管理系统 - 主JS文件

// 为所有确认操作添加防误触
document.addEventListener('DOMContentLoaded', function() {
    // 为所有带 data-confirm 属性的链接添加确认对话框
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // 自动隐藏消息提示
    setTimeout(() => {
        document.querySelectorAll('.alert-dismissible').forEach(el => {
            const bsAlert = new bootstrap.Alert(el);
            bsAlert.close();
        });
    }, 5000);

    // 通知轮询
    checkNotifications();
    setInterval(checkNotifications, 30000);
});

function checkNotifications() {
    fetch('/notifications/unread-count/')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('notiBadge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'flex';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(() => {});
}

// Toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;';
        document.body.appendChild(container);
    }
    
    const colors = {
        success: '#7BC67E',
        error: '#FF6B6B',
        warning: '#FFB347',
        info: '#6CB4EE',
    };
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: ${colors[type] || colors.info};
        color: #fff;
        padding: 12px 24px;
        border-radius: 12px;
        margin-bottom: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease;
        font-weight: 500;
    `;
    toast.textContent = message;
    document.getElementById('toastContainer').appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
