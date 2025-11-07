/**
 * SIGMA-PLI - M00: Home - Navigation
 * Gerencia a navegação e interações do menu
 */

class NavigationManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupMobileMenu();
        this.setupScrollEffects();
        this.setupSmoothScrolling();
    }

    setupMobileMenu() {
        // Criar botão de toggle para mobile (se necessário)
        const nav = document.querySelector('.sigma-nav');
        const menu = document.querySelector('.nav-menu');
        // Se não existir nav ou menu no template atual, não faz nada
        if (!nav || !menu) return;

        if (window.innerWidth <= 768) {
            // Adicionar classe para esconder menu inicialmente
            if (!menu.classList.contains('mobile-hidden')) menu.classList.add('mobile-hidden');

            // Criar botão toggle (evita múltiplos botões se já existir)
            let toggleBtn = nav.querySelector('.nav-toggle');
            if (!toggleBtn) {
                toggleBtn = document.createElement('button');
                toggleBtn.className = 'nav-toggle';
                toggleBtn.innerHTML = '☰';
                toggleBtn.setAttribute('aria-label', 'Toggle navigation');
                nav.appendChild(toggleBtn);
            }

            // Event listener para toggle (idempotente)
            toggleBtn.addEventListener('click', () => {
                menu.classList.toggle('mobile-hidden');
                toggleBtn.innerHTML = menu.classList.contains('mobile-hidden') ? '☰' : '✕';
            });

            // Fechar menu ao clicar em link (se houver links)
            menu.addEventListener('click', (e) => {
                if (e.target && e.target.classList && e.target.classList.contains('nav-link')) {
                    menu.classList.add('mobile-hidden');
                    toggleBtn.innerHTML = '☰';
                }
            });
        }
    }

    setupScrollEffects() {
        let lastScrollTop = 0;
        const header = document.querySelector('.sigma-header');

        if (!header) return; // nada a fazer se não existir header

        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            // Adicionar/remover classe scrolled
            if (scrollTop > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }

            // Esconder/mostrar header no scroll
            try {
                if (scrollTop > lastScrollTop && scrollTop > 200) {
                    header.style.transform = 'translateY(-100%)';
                } else {
                    header.style.transform = 'translateY(0)';
                }
            } catch (e) {
                // Algumas implementações podem não permitir style modification; silencia erros
            }

            lastScrollTop = scrollTop;
        });
    }

    setupSmoothScrolling() {
        // Smooth scroll para links internos
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const selector = this.getAttribute('href');
                if (!selector) return;
                const target = document.querySelector(selector);

                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Utilitários de navegação
class NavigationUtils {
    static highlightCurrentSection() {
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('.nav-link');

        const observerOptions = {
            root: null,
            rootMargin: '-50% 0px -50% 0px',
            threshold: 0
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === `#${id}`) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }, observerOptions);

        sections.forEach(section => {
            if (section.id) {
                observer.observe(section);
            }
        });
    }

    static setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // ESC para fechar menu mobile
            if (e.key === 'Escape') {
                const menu = document.querySelector('.nav-menu');
                const toggle = document.querySelector('.nav-toggle');
                if (menu && !menu.classList.contains('mobile-hidden')) {
                    menu.classList.add('mobile-hidden');
                    if (toggle) toggle.innerHTML = '☰';
                }
            }
        });
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new NavigationManager();
    NavigationUtils.highlightCurrentSection();
    NavigationUtils.setupKeyboardNavigation();
});