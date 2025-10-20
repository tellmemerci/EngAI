class NotificationManager {
    constructor() {
        this.socket = null;
        this.notificationCount = 0;
        this.notifications = [];
        this.badge = document.getElementById('notificationBadge');
        this.container = document.querySelector('.notifications-wrapper');
        this.setupWebSocket();
        this.setupEventListeners();
    }

    setupWebSocket() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.socket = new WebSocket(
            `${wsScheme}://${window.location.host}/ws/notifications/`
        );

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
            // Попытка переподключения через 5 секунд
            setTimeout(() => this.setupWebSocket(), 5000);
        };
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            const notificationItem = e.target.closest('.notification-item');
            if (notificationItem && !notificationItem.classList.contains('read')) {
                this.markAsRead(notificationItem.dataset.id);
            }
        });

        const markAllReadBtn = document.querySelector('.mark-all-read');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => this.markAllAsRead());
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'notification':
                this.addNotification(data.notification);
                break;
            case 'notification_read':
                this.updateNotificationStatus(data.notification_id);
                break;
        }
    }

    addNotification(notification) {
        // Добавляем уведомление в начало списка
        this.notifications.unshift(notification);
        this.updateNotificationCount();
        this.renderNotification(notification);
        this.showToast(notification);
    }

    renderNotification(notification) {
        const template = `
            <div class="notification-item ${notification.is_read ? 'read' : 'unread'}" 
                 data-id="${notification.id}">
                <div class="notification-icon" style="color: ${notification.color}">
                    <i class="bi ${notification.icon_class}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-header">
                        <h3 class="notification-title">${notification.title}</h3>
                        <span class="notification-date">${notification.created_at}</span>
                    </div>
                    <p class="notification-text">${notification.text}</p>
                    ${notification.image ? 
                        `<img src="${notification.image}" alt="" class="notification-image">` : 
                        ''}
                </div>
                <div class="notification-status"></div>
            </div>
        `;

        if (this.container) {
            const noNotifications = this.container.querySelector('.no-notifications');
            if (noNotifications) {
                noNotifications.remove();
            }
            this.container.insertAdjacentHTML('afterbegin', template);
        }
    }

    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = `notification ${notification.notification_type}`;
        toast.innerHTML = `
            <div class="notification-icon">
                <i class="bi ${notification.icon_class}"></i>
            </div>
            <div class="notification-text">${notification.title}</div>
            <button class="close-notification">
                <i class="bi bi-x"></i>
            </button>
        `;

        document.body.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('show'));

        const closeBtn = toast.querySelector('.close-notification');
        closeBtn.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    markAsRead(notificationId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'mark_as_read',
                notification_id: notificationId
            }));
        }
    }

    markAllAsRead() {
        const unreadNotifications = document.querySelectorAll('.notification-item.unread');
        unreadNotifications.forEach(notification => {
            this.markAsRead(notification.dataset.id);
        });
    }

    updateNotificationStatus(notificationId) {
        const notification = document.querySelector(`.notification-item[data-id="${notificationId}"]`);
        if (notification) {
            notification.classList.remove('unread');
            notification.classList.add('read');
            this.updateNotificationCount();
        }
    }

    updateNotificationCount() {
        const unreadCount = document.querySelectorAll('.notification-item.unread').length;
        if (this.badge) {
            this.badge.textContent = unreadCount;
            this.badge.style.display = unreadCount > 0 ? 'block' : 'none';
        }

        const counter = document.querySelector('.notification-counter');
        if (counter) {
            counter.textContent = `${unreadCount} непрочитанных`;
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
}); 