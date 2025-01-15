particlesJS('particles-js', {
    particles: {
        number: {
            value: 300, // Количество частиц
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
            value: 0.5, // Меньшая прозрачность для точек
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

document.addEventListener("DOMContentLoaded", function () {
    // Найти контейнер с данными
    const dataContainer = document.getElementById("data-container");

    // Извлечь данные из атрибутов
    const movementStats = JSON.parse(dataContainer.dataset.movementStats);
    const peakHourData = JSON.parse(dataContainer.dataset.peakHour);

    // Теперь можно использовать данные для построения графиков
    console.log(movementStats);
    console.log(peakHourData);

    // Пример использования с Chart.js
    const ctx = document.getElementById("myChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(movementStats),
            datasets: [{
                label: "Movement Statistics",
                data: Object.values(movementStats),
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
            }]
        },
    });
});


document.getElementById("file-input").addEventListener("change", function(event) {
    const fileName = event.target.files[0].name;
    document.getElementById("file-name").innerText = fileName;
});

