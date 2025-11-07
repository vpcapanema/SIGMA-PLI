/**
 * SIGMA-PLI M07 - Ferramentas Hub
 * Animações e interatividade para a página de ferramentas
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    initFilterButtons();
    initCardAnimations();
});

/**
 * Inicializa animações ao fazer scroll
 */
function initScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }
    );

    // Observar todos os cards
    const cards = document.querySelectorAll('.app-card');
    cards.forEach((card, index) => {
        // Adicionar delay progressivo
        card.style.transitionDelay = `${index * 0.1}s`;
        observer.observe(card);
    });

    // Adicionar animação de entrada aos cards
    setTimeout(() => {
        cards.forEach((card) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
        });
    }, 100);
}

/**
 * Inicializa botões de filtro
 */
function initFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const appCards = document.querySelectorAll('.app-card');

    filterButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const filter = button.getAttribute('data-filter');

            // Atualizar botão ativo
            filterButtons.forEach((btn) => btn.classList.remove('active'));
            button.classList.add('active');

            // Filtrar cards com animação
            appCards.forEach((card, index) => {
                const category = card.getAttribute('data-category');

                if (filter === 'all' || category === filter) {
                    // Mostrar card com delay progressivo
                    setTimeout(() => {
                        card.classList.remove('hidden');
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(30px)';

                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0)';
                        }, 50);
                    }, index * 100);
                } else {
                    // Esconder card
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(30px)';
                    setTimeout(() => {
                        card.classList.add('hidden');
                    }, 300);
                }
            });

            // Adicionar efeito de ripple no botão
            createRipple(button, event);
        });
    });
}

/**
 * Inicializa animações dos cards
 */
function initCardAnimations() {
    const cards = document.querySelectorAll('.app-card');

    cards.forEach((card) => {
        // Efeito parallax no ícone
        card.addEventListener('mousemove', (e) => {
            const icon = card.querySelector('.app-icon');
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;

            icon.style.transform = `translate(${deltaX * 10}px, ${deltaY * 10}px) scale(1.05)`;
        });

        card.addEventListener('mouseleave', () => {
            const icon = card.querySelector('.app-icon');
            icon.style.transform = 'translate(0, 0) scale(1)';
        });

        // Efeito de brilho nas tags
        const tags = card.querySelectorAll('.tag');
        tags.forEach((tag, index) => {
            card.addEventListener('mouseenter', () => {
                setTimeout(() => {
                    tag.style.transform = 'translateY(-2px)';
                    tag.style.boxShadow = '0 4px 8px rgba(44, 143, 255, 0.3)';
                }, index * 50);
            });

            card.addEventListener('mouseleave', () => {
                tag.style.transform = 'translateY(0)';
                tag.style.boxShadow = 'none';
            });
        });
    });
}

/**
 * Cria efeito ripple em um elemento
 */
function createRipple(element, event) {
    const circle = document.createElement('span');
    const diameter = Math.max(element.clientWidth, element.clientHeight);
    const radius = diameter / 2;

    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - element.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - element.offsetTop - radius}px`;
    circle.classList.add('ripple');

    const rippleStyle = document.createElement('style');
    rippleStyle.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple-animation 0.6s ease-out;
            pointer-events: none;
        }
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;

    if (!document.querySelector('style[data-ripple]')) {
        rippleStyle.setAttribute('data-ripple', 'true');
        document.head.appendChild(rippleStyle);
    }

    const ripple = element.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }

    element.appendChild(circle);

    setTimeout(() => {
        circle.remove();
    }, 600);
}

/**
 * Animação de contador para estatísticas (se necessário no futuro)
 */
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);

    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start);
        }
    }, 16);
}

/**
 * Adiciona efeito de partículas no hero (opcional - pode ser removido se pesado)
 */
function initParticles() {
    const hero = document.querySelector('.ferramentas-hero');
    if (!hero) return;

    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(44, 143, 255, 0.6);
            border-radius: 50%;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            animation: float ${3 + Math.random() * 4}s ease-in-out infinite;
            animation-delay: ${Math.random() * 2}s;
        `;
        hero.appendChild(particle);
    }

    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
        @keyframes float {
            0%, 100% {
                transform: translateY(0) translateX(0);
                opacity: 0;
            }
            50% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) translateX(${Math.random() > 0.5 ? '' : '-'}50px);
            }
        }
    `;
    document.head.appendChild(styleSheet);
}

// Inicializar partículas (comentar se deixar a página lenta)
// initParticles();

/**
 * Smooth scroll para links internos (se houver)
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/**
 * Log de analytics (placeholder - integrar com sistema real se necessário)
 */
function trackAppClick(appName) {
    console.log(`📊 App clicado: ${appName}`);
    // Aqui você pode integrar com Google Analytics, Matomo, etc.
}

// Adicionar tracking aos botões de acesso
document.querySelectorAll('.btn-primary').forEach(button => {
    button.addEventListener('click', (e) => {
        const card = e.target.closest('.app-card');
        const appName = card.querySelector('.app-title').textContent;
        trackAppClick(appName);
    });
});

console.log('✅ M07 Ferramentas Hub - Scripts carregados com sucesso!');
