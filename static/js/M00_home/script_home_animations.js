/**
 * SIGMA-PLI - M00: Home - Animations
 * Gerencia animações e efeitos visuais da página
 */

class AnimationManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupLoadingAnimations();
        this.setupHoverEffects();
    }

    setupIntersectionObserver() {
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observar elementos que devem ser animados
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    setupLoadingAnimations() {
        // Animação de fade-in no carregamento da página
        document.body.classList.add('loading');

        window.addEventListener('load', () => {
            setTimeout(() => {
                document.body.classList.remove('loading');
                document.body.classList.add('loaded');
            }, 100);
        });
    }

    setupHoverEffects() {
        // Efeitos de hover para cards e botões
        document.querySelectorAll('.card, .btn-primary, .btn-secondary').forEach(el => {
            el.addEventListener('mouseenter', this.handleHoverEnter.bind(this));
            el.addEventListener('mouseleave', this.handleHoverLeave.bind(this));
        });
    }

    handleHoverEnter(e) {
        const element = e.currentTarget;

        // Adicionar classe de hover
        element.classList.add('hover-active');

        // Efeito de scale para cards
        if (element.classList.contains('card')) {
            element.style.transform = 'translateY(-5px) scale(1.02)';
        }

        // Efeito de glow para botões
        if (element.classList.contains('btn-primary') || element.classList.contains('btn-secondary')) {
            element.style.boxShadow = '0 0 20px rgba(0, 123, 255, 0.3)';
        }
    }

    handleHoverLeave(e) {
        const element = e.currentTarget;

        // Remover classe de hover
        element.classList.remove('hover-active');

        // Resetar transform
        element.style.transform = '';
        element.style.boxShadow = '';
    }
}

// Utilitários de animação
class AnimationUtils {
    static fadeIn(element, duration = 500) {
        element.style.opacity = '0';
        element.style.display = 'block';

        const start = performance.now();

        const fade = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = elapsed / duration;

            if (progress < 1) {
                element.style.opacity = progress;
                requestAnimationFrame(fade);
            } else {
                element.style.opacity = '1';
            }
        };

        requestAnimationFrame(fade);
    }

    static fadeOut(element, duration = 500) {
        const start = performance.now();
        const startOpacity = parseFloat(getComputedStyle(element).opacity);

        const fade = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = elapsed / duration;

            if (progress < 1) {
                element.style.opacity = startOpacity * (1 - progress);
                requestAnimationFrame(fade);
            } else {
                element.style.opacity = '0';
                element.style.display = 'none';
            }
        };

        requestAnimationFrame(fade);
    }

    static slideIn(element, direction = 'up', duration = 500) {
        const directions = {
            up: 'translateY(100%)',
            down: 'translateY(-100%)',
            left: 'translateX(100%)',
            right: 'translateX(-100%)'
        };

        element.style.transform = directions[direction];
        element.style.opacity = '0';
        element.style.display = 'block';

        const start = performance.now();

        const slide = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = elapsed / duration;

            if (progress < 1) {
                const easeProgress = this.easeOutCubic(progress);
                element.style.transform = `translateY(${100 * (1 - easeProgress)}%)`;
                element.style.opacity = easeProgress;
                requestAnimationFrame(slide);
            } else {
                element.style.transform = 'translateY(0)';
                element.style.opacity = '1';
            }
        };

        requestAnimationFrame(slide);
    }

    static easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    static createRippleEffect(event) {
        const button = event.currentTarget;
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
        circle.classList.add('ripple-effect');

        const ripple = button.getElementsByClassName('ripple-effect')[0];

        if (ripple) {
            ripple.remove();
        }

        button.appendChild(circle);

        setTimeout(() => {
            circle.remove();
        }, 600);
    }
}

// Efeitos especiais para o hero banner
class HeroAnimations {
    static init() {
        this.setupTypingEffect();
        this.setupParticleEffect();
        this.setupParallax();
    }

    static setupTypingEffect() {
    const text = "SIGMA-PLI — Sistema Integrado de Gestão, Monitoramento e Apoio Técnico";
        const element = document.querySelector('.hero-title');
        let index = 0;

        if (element) {
            element.textContent = '';

            const typeWriter = () => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                    setTimeout(typeWriter, 50);
                }
            };

            setTimeout(typeWriter, 1000);
        }
    }

    static setupParticleEffect() {
        const canvas = document.createElement('canvas');
        canvas.className = 'hero-particles';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const hero = document.querySelector('.hero');
        if (hero) {
            hero.appendChild(canvas);

            const ctx = canvas.getContext('2d');
            const particles = [];

            for (let i = 0; i < 50; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 2,
                    vy: (Math.random() - 0.5) * 2,
                    size: Math.random() * 2 + 1
                });
            }

            const animate = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                particles.forEach(particle => {
                    particle.x += particle.vx;
                    particle.y += particle.vy;

                    if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
                    if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

                    ctx.beginPath();
                    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(0, 123, 255, 0.1)';
                    ctx.fill();
                });

                requestAnimationFrame(animate);
            };

            animate();
        }
    }

    static setupParallax() {
        const hero = document.querySelector('.hero');

        if (hero) {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;

                hero.style.transform = `translateY(${rate}px)`;
            });
        }
    }
}

// Inicializar animações quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new AnimationManager();
    HeroAnimations.init();

    // Adicionar efeito ripple aos botões
    document.querySelectorAll('.btn-primary, .btn-secondary').forEach(btn => {
        btn.addEventListener('click', AnimationUtils.createRippleEffect);
    });
});