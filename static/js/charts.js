// SkillBridge Chart.js Renderers

function initReadinessChart(canvasId, components) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Technical Coverage', 'Skill Quality', 'Soft Skills', 'Learning Progress'],
            datasets: [{
                label: 'Score Breakdown (%)',
                data: [
                    components.technical_coverage,
                    components.skill_quality,
                    components.soft_skills,
                    components.learning_progress
                ],
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3B82F6',
                borderWidth: 2,
                pointBackgroundColor: '#1D4ED8',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: { stepSize: 20, display: false },
                    grid: { color: '#E5E7EB' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function initHistoryChart(canvasId, historyData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = [];
    const scores = [];

    // Flatten history items
    Object.keys(historyData).forEach(skill => {
        historyData[skill].forEach(item => {
            labels.push(`${skill} (${item.date})`);
            scores.push(item.score);
        });
    });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.length ? labels : ['No Assessments'],
            datasets: [{
                label: 'Verified Score (%)',
                data: scores.length ? scores : [0],
                borderColor: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.3,
                borderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0, max: 100, grid: { color: '#F3F4F6' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function initInstitutionAnalytics(data) {
    // 1. Common Skill Gaps
    const c1 = document.getElementById('chartSkillGaps');
    if (c1 && data.chart1.labels.length > 0) {
        new Chart(c1, {
            type: 'bar',
            data: {
                labels: data.chart1.labels,
                datasets: [{
                    label: 'Students with Gap',
                    data: data.chart1.data,
                    backgroundColor: '#EF4444',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: '#F3F4F6' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. Career Goal Distribution
    const c2 = document.getElementById('chartCareerGoals');
    if (c2 && data.chart2.labels.length > 0) {
        new Chart(c2, {
            type: 'doughnut',
            data: {
                labels: data.chart2.labels,
                datasets: [{
                    data: data.chart2.data,
                    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#6366F1']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // 3. Assessment Completion
    const c3 = document.getElementById('chartAssessmentRate');
    if (c3) {
        new Chart(c3, {
            type: 'pie',
            data: {
                labels: data.chart3.labels,
                datasets: [{
                    data: data.chart3.data,
                    backgroundColor: ['#10B981', '#E5E7EB']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // 4. Internship Participation
    const c4 = document.getElementById('chartInternshipParticipation');
    if (c4) {
        new Chart(c4, {
            type: 'doughnut',
            data: {
                labels: data.chart4.labels,
                datasets: [{
                    data: data.chart4.data,
                    backgroundColor: ['#10B981', '#3B82F6', '#D1D5DB']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // 5. Career Readiness Distribution
    const c5 = document.getElementById('chartReadinessDistribution');
    if (c5) {
        new Chart(c5, {
            type: 'bar',
            data: {
                labels: data.chart5.labels,
                datasets: [{
                    label: 'Students in Range',
                    data: data.chart5.data,
                    backgroundColor: '#3B82F6',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: '#F3F4F6' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 6. Industry Demanded Skills
    const c6 = document.getElementById('chartIndustryDemands');
    if (c6 && data.chart6.labels.length > 0) {
        new Chart(c6, {
            type: 'bar',
            data: {
                labels: data.chart6.labels,
                datasets: [{
                    label: 'Opportunity Requirements',
                    data: data.chart6.data,
                    backgroundColor: '#8B5CF6',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { beginAtZero: true, grid: { color: '#F3F4F6' } },
                    y: { grid: { display: false } }
                }
            }
        });
    }
}
