// Initialize charts for habit progress visualization
function initializeHabitChart(elementId, streak, goal) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [streak, goal - streak],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(200, 200, 200, 0.2)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
}

// Initialize progress bars with animation
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = targetWidth;
        }, 100);
    });
}

// Update streak counter with animation
function updateStreakCounter(element, targetStreak) {
    const duration = 1000;
    const steps = 20;
    const stepTime = duration / steps;
    let currentStreak = 0;

    const interval = setInterval(() => {
        currentStreak += targetStreak / steps;
        if (currentStreak >= targetStreak) {
            element.textContent = targetStreak;
            clearInterval(interval);
        } else {
            element.textContent = Math.floor(currentStreak);
        }
    }, stepTime);
}

// Initialize all visualizations
document.addEventListener('DOMContentLoaded', () => {
    // Initialize progress bars with animation
    initializeProgressBars();

    // Initialize streak counters
    document.querySelectorAll('.streak-counter').forEach(counter => {
        const targetStreak = parseInt(counter.dataset.streak || 0);
        updateStreakCounter(counter, targetStreak);
    });

    // Initialize habit charts
    document.querySelectorAll('.habit-chart').forEach(chart => {
        const streak = parseInt(chart.dataset.streak || 0);
        const goal = parseInt(chart.dataset.goal || 7);
        initializeHabitChart(chart.id, streak, goal);
    });
});