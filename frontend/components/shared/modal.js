/**
 * Modal Component - Reusable modal system
 */

class ModalComponent {
    constructor() {
        this.currentModal = null;
        this.init();
    }

    init() {
        this.createModalContainer();
        this.bindEvents();
    }

    createModalContainer() {
        // Create modal container if it doesn't exist
        if (!document.getElementById('modal-container')) {
            const container = document.createElement('div');
            container.id = 'modal-container';
            container.innerHTML = `
                <div class="modal-overlay" style="display: none;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3 class="modal-title"></h3>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body"></div>
                        <div class="modal-footer"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(container);
            
            // Add modal styles
            this.addModalStyles();
        }
    }

    addModalStyles() {
        const styles = `
            <style>
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .modal-content {
                    background: white;
                    border-radius: 8px;
                    max-width: 90%;
                    max-height: 90%;
                    overflow: auto;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }
                
                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid #e0e0e0;
                }
                
                .modal-title {
                    margin: 0;
                    color: #333;
                }
                
                .modal-close {
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #666;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .modal-close:hover {
                    color: #333;
                }
                
                .modal-body {
                    padding: 20px;
                }
                
                .modal-footer {
                    padding: 15px 20px;
                    border-top: 1px solid #e0e0e0;
                    display: flex;
                    justify-content: flex-end;
                    gap: 10px;
                }
            </style>
        `;
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-close') || e.target.matches('.modal-overlay')) {
                this.close();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.close();
            }
        });
    }

    show(options = {}) {
        const overlay = document.querySelector('.modal-overlay');
        const title = document.querySelector('.modal-title');
        const body = document.querySelector('.modal-body');
        const footer = document.querySelector('.modal-footer');

        if (overlay && title && body && footer) {
            title.textContent = options.title || 'Modal';
            body.innerHTML = options.body || '';
            footer.innerHTML = options.footer || '';
            
            overlay.style.display = 'flex';
            this.currentModal = options;
        }
    }

    close() {
        const overlay = document.querySelector('.modal-overlay');
        if (overlay) {
            overlay.style.display = 'none';
            this.currentModal = null;
        }
    }

    confirm(message, title = 'Confirm') {
        return new Promise((resolve) => {
            this.show({
                title: title,
                body: `<p>${message}</p>`,
                footer: `
                    <button class="btn btn-secondary modal-cancel">Cancel</button>
                    <button class="btn btn-danger modal-confirm">Confirm</button>
                `
            });

            const handleClick = (e) => {
                if (e.target.matches('.modal-confirm')) {
                    document.removeEventListener('click', handleClick);
                    this.close();
                    resolve(true);
                } else if (e.target.matches('.modal-cancel')) {
                    document.removeEventListener('click', handleClick);
                    this.close();
                    resolve(false);
                }
            };

            document.addEventListener('click', handleClick);
        });
    }
}

// Initialize modal when loaded
window.modalComponent = new ModalComponent();
console.log('✅ Modal component loaded');