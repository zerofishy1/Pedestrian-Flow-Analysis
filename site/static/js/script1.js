// Инициализация анимации фона для страницы с результатами
particlesJS('particles-js', {
    particles: {
        number: {
            value: 300,
            density: {
                enable: true,
                value_area: 800
            }
        },
        color: {
            value: "#00e6e6"
        },
        shape: {
            type: "circle",
            stroke: {
                width: 0,
                color: "#000000"
            }
        },
        opacity: {
            value: 0.5,
            random: true,
            anim: {
                enable: false
            }
        },
        size: {
            value: 2,
            random: true,
            anim: {
                enable: true,
                speed: 3,
                size_min: 0.3
            }
        },
        line_linked: {
            enable: true,
            distance: 100,
            color: "#00e6e6",
            opacity: 0.2,
            width: 1
        },
        move: {
            enable: true,
            speed: 2,
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


// Анимация увеличения числа
document.addEventListener("DOMContentLoaded", () => {
    const countElement = document.getElementById("unique-people-count");
    if (countElement) {
        const targetCount = parseInt(countElement.dataset.count, 10);
        let currentCount = 0;
        const duration = 1000; // Продолжительность анимации в миллисекундах
        const startTime = performance.now();

        const updateCount = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1); // Прогресс от 0 до 1
            currentCount = Math.floor(targetCount * progress);

            countElement.textContent = currentCount;

            if (progress < 1) {
                requestAnimationFrame(updateCount);
            }
        };

        requestAnimationFrame(updateCount);
    }
});


// Запуск анимации диаграммы
document.addEventListener("DOMContentLoaded", () => {
    const bars = document.querySelectorAll(".bar");
    let maxValue = 0;

    // Найти максимальное значение
    bars.forEach((bar) => {
        const height = parseInt(bar.style.getPropertyValue("--height"), 10) || 0;
        if (height > maxValue) {
            maxValue = height;
        }
    });

    // Установить высоту столбцов на основе максимального значения
    bars.forEach((bar) => {
        const height = parseInt(bar.style.getPropertyValue("--height"), 10) || 0;
        bar.style.height = `${230 * (height / maxValue)}px`; // Масштаб высоты столбцов
    });
});

document.getElementById('saveBtn').addEventListener('click', function () {
    var node = document.body;

    html2canvas(node).then(function (canvas) {
        // Создайте новый Canvas с заданными размерами
        var croppedCanvas = document.createElement('canvas');
        var ctx = croppedCanvas.getContext('2d');

        var cropX = 630; // Начальная точка по X
        var cropY = 0;  // Начальная точка по Y
        var cropWidth = 660;  // Ширина обрезки
        var cropHeight = 780; // Высота обрезки

        croppedCanvas.width = cropWidth;
        croppedCanvas.height = cropHeight;

        // Обрезка изображения
        ctx.drawImage(canvas, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);

        // Сохранение обрезанного изображения
        croppedCanvas.toBlob(function (blob) {
            var link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'cropped-screenshot.png';
            link.click();
        });
    });
});
