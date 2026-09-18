// Distraction-Free Skill Assessment Runner

class AssessmentRunner {
    constructor(questions, assessmentId, serverEvalData, timeLimitMinutes = 20) {
        this.questions = questions;
        this.assessmentId = assessmentId;
        this.serverEvalData = serverEvalData;
        this.currentIndex = 0;
        this.answers = {}; // qId -> optionIndex
        this.timeRemaining = timeLimitMinutes * 60;
        this.timerInterval = null;

        this.initElements();
        this.initTimer();
        this.renderQuestion();
    }

    initElements() {
        this.progressText = document.getElementById('assessProgressText');
        this.progressBar = document.getElementById('assessProgressBar');
        this.timerText = document.getElementById('assessTimer');
        this.questionContainer = document.getElementById('assessQuestionContainer');
        this.btnPrev = document.getElementById('btnAssessPrev');
        this.btnNext = document.getElementById('btnAssessNext');
        this.btnSubmit = document.getElementById('btnAssessSubmit');

        this.btnPrev.addEventListener('click', () => this.navigate(-1));
        this.btnNext.addEventListener('click', () => this.navigate(1));
        this.btnSubmit.addEventListener('click', () => this.confirmSubmit());
    }

    initTimer() {
        this.updateTimerDisplay();
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            if (this.timeRemaining <= 0) {
                clearInterval(this.timerInterval);
                alert('Time expired! Submitting your assessment answers automatically.');
                this.submitExam();
            }
        }, 1000);
    }

    updateTimerDisplay() {
        const mins = Math.floor(this.timeRemaining / 60);
        const secs = this.timeRemaining % 60;
        this.timerText.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        if (this.timeRemaining < 180) {
            this.timerText.className = 'fw-bold text-danger';
        }
    }

    renderQuestion() {
        const q = this.questions[this.currentIndex];
        const total = this.questions.length;

        // Progress bar
        this.progressText.textContent = `Question ${this.currentIndex + 1} of ${total}`;
        const pct = Math.round(((this.currentIndex + 1) / total) * 100);
        this.progressBar.style.width = `${pct}%`;

        // Render card
        let optionsHtml = '';
        q.options.forEach((opt, idx) => {
            const isChecked = this.answers[q.id] === idx ? 'checked' : '';
            optionsHtml += `
                <div class="form-check p-3 mb-2 border rounded-3 bg-white option-card ${isChecked ? 'border-primary bg-light' : ''}" style="cursor: pointer;" onclick="document.getElementById('opt_${q.id}_${idx}').click();">
                    <input class="form-check-input ms-0 me-3" type="radio" name="question_${q.id}" id="opt_${q.id}_${idx}" value="${idx}" ${isChecked}>
                    <label class="form-check-label w-100 fw-medium" for="opt_${q.id}_${idx}" style="cursor: pointer;">
                        ${opt}
                    </label>
                </div>
            `;
        });

        this.questionContainer.innerHTML = `
            <div class="mb-3">
                <span class="badge bg-light text-secondary border mb-2">${q.topic || 'General'}</span>
                <h5 class="fw-semibold lh-base mb-4">${q.question_text}</h5>
                <div class="options-group">
                    ${optionsHtml}
                </div>
            </div>
        `;

        // Bind radio change listeners
        q.options.forEach((_, idx) => {
            const radio = document.getElementById(`opt_${q.id}_${idx}`);
            if (radio) {
                radio.addEventListener('change', () => {
                    this.answers[q.id] = idx;
                    this.renderQuestion();
                });
            }
        });

        // Navigation buttons
        this.btnPrev.disabled = this.currentIndex === 0;
        if (this.currentIndex === total - 1) {
            this.btnNext.classList.add('d-none');
            this.btnSubmit.classList.remove('d-none');
        } else {
            this.btnNext.classList.remove('d-none');
            this.btnSubmit.classList.add('d-none');
        }
    }

    navigate(delta) {
        const nextIdx = this.currentIndex + delta;
        if (nextIdx >= 0 && nextIdx < this.questions.length) {
            this.currentIndex = nextIdx;
            this.renderQuestion();
        }
    }

    confirmSubmit() {
        const answeredCount = Object.keys(this.answers).length;
        const total = this.questions.length;
        let warningText = 'Are you sure you want to finalize and submit? You cannot change your answers after submission.';
        if (answeredCount < total) {
            warningText = `You have answered ${answeredCount} of ${total} questions. Unanswered questions will be counted as incorrect. Submit now?`;
        }

        if (confirm(warningText)) {
            this.submitExam();
        }
    }

    async submitExam() {
        clearInterval(this.timerInterval);
        this.btnSubmit.disabled = true;
        this.btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Evaluating...';

        try {
            const res = await fetch('/student/assessment/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    assessment_id: this.assessmentId,
                    answers: this.answers,
                    eval_data: this.serverEvalData
                })
            });

            const result = await res.json();
            if (result.success) {
                window.location.href = result.redirect_url;
            } else {
                alert(result.message || 'Submission failed. Please check connection and try again.');
                this.btnSubmit.disabled = false;
                this.btnSubmit.textContent = 'Submit Assessment';
            }
        } catch (err) {
            console.error(err);
            alert('Submission network error. Please try again.');
            this.btnSubmit.disabled = false;
            this.btnSubmit.textContent = 'Submit Assessment';
        }
    }
}
