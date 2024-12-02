particlesJS('particles-js', {
    particles: {
        number: {
            value: 250, // Количество частиц
            density: {
                enable: true,
                value_area: 800
            }
        },
        color: {
            value: "#00e6e6" // Цвет частиц — яркий голубой
        },
        shape: {
            type: "circle",
            stroke: {
                width: 0,
                color: "#000000"
            }
        },
        opacity: {
            value: 0.3, // Меньшая прозрачность для точек
            random: true,
            anim: {
                enable: false
            }
        },
        size: {
            value: 2, // Уменьшаем размер точек
            random: true,
            anim: {
                enable: true,
                speed: 3,
                size_min: 0.3
            }
        },
        line_linked: {
            enable: true,
            distance: 100, // Расстояние между точками
            color: "#00e6e6", // Яркие линии
            opacity: 0.2, // Тусклые линии, но не слишком
            width: 1
        },
        move: {
            enable: true,
            speed: 2, // Ускоряем движение
            direction: "none",
            random: false,
            straight: false,
            out_mode: "out",
            bounce: false,
            attract: {
                enable: false,
                rotateX: 600,
                rotateY: 1200
            }
        }
    },
    interactivity: {
        detect_on: "canvas",
        events: {
            onhover: {
                enable: true,
                mode: "grab"
            },
            onclick: {
                enable: true,
                mode: "push"
            },
            resize: true
        },
        modes: {
            grab: {
                distance: 200,
                line_linked: {
                    opacity: 0.5
                }
            },
            push: {
                particles_nb: 4
            }
        }
    },
    retina_detect: true
});
