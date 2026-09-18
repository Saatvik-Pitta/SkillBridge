// SkillBridge Global Client Interactions & Modals

document.addEventListener('DOMContentLoaded', () => {
    // Mobile sidebar toggle
    const toggleBtn = document.getElementById('mobileSidebarToggle');
    const sidebar = document.querySelector('.app-sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show-mobile');
        });
    }

    // Initialize Opportunity View Details Modal Handler
    initOpportunityModals();

    // Initialize Industry Candidate Modal Handler
    initCandidateModals();

    // Initialize Notification Read Buttons
    initNotificationHandlers();
});

function initOpportunityModals() {
    const oppModalEl = document.getElementById('opportunityDetailsModal');
    if (!oppModalEl) return;
    const oppModal = new bootstrap.Modal(oppModalEl);

    document.querySelectorAll('.btn-view-opportunity').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const oppId = btn.dataset.oppId;
            if (!oppId) return;

            try {
                const res = await fetch(`/student/api/opportunity/${oppId}/details`);
                if (!res.ok) throw new Error('Failed to fetch details');
                const data = await res.json();

                // Populate modal
                document.getElementById('modalOppTitle').textContent = data.title;
                document.getElementById('modalOppCompany').textContent = data.company_name;
                document.getElementById('modalOppMeta').textContent = `${data.opportunity_type} · ${data.location} · ${data.work_mode} · ${data.duration}`;
                document.getElementById('modalOppDesc').textContent = data.description;
                document.getElementById('modalOppDeadline').textContent = data.deadline;
                document.getElementById('modalOppStipend').textContent = data.stipend_salary;
                document.getElementById('modalOppEligibility').textContent = data.eligibility;
                document.getElementById('modalOppSource').href = data.source_url;
                document.getElementById('modalOppDateRetrieved').textContent = data.date_retrieved;

                // Match percentage badge
                const matchEl = document.getElementById('modalOppMatchScore');
                matchEl.textContent = `${data.match_percentage}%`;
                matchEl.className = 'badge ' + (data.match_percentage >= 70 ? 'bg-success' : data.match_percentage >= 40 ? 'bg-primary' : 'bg-warning text-dark');

                // Why You Match list
                const whyList = document.getElementById('modalOppWhyMatch');
                whyList.innerHTML = '';
                if (data.why_match && data.why_match.length > 0) {
                    data.why_match.forEach(item => {
                        const li = document.createElement('li');
                        li.className = 'text-success small mb-1';
                        li.textContent = item;
                        whyList.appendChild(li);
                    });
                } else {
                    whyList.innerHTML = '<li class="small text-muted">Complete assessments to increase verified match rate.</li>';
                }

                // Skills to improve list
                const gapList = document.getElementById('modalOppGapSkills');
                gapList.innerHTML = '';
                if (data.gap_skills && data.gap_skills.length > 0) {
                    data.gap_skills.forEach(item => {
                        const li = document.createElement('li');
                        li.className = 'text-danger small mb-1';
                        li.textContent = `✗ ${item.skill} (Need ${item.target}, ${item.score !== null ? 'have ' + item.score : 'Not Assessed'})`;
                        gapList.appendChild(li);
                    });
                } else {
                    gapList.innerHTML = '<li class="small text-success">✓ You satisfy all required skill benchmarks!</li>';
                }

                // Required skills tags
                const reqSkillsList = document.getElementById('modalOppReqSkills');
                reqSkillsList.innerHTML = '';
                data.required_skills.forEach((sk, idx) => {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-light text-dark border me-1 mb-1';
                    const lvl = data.required_skill_levels[idx] || 'Intermediate';
                    badge.textContent = `${sk} (${lvl})`;
                    reqSkillsList.appendChild(badge);
                });

                // Apply button setup
                const applyBtn = document.getElementById('modalBtnApply');
                const alreadyAppliedBadge = document.getElementById('modalAlreadyAppliedNotice');

                if (data.has_applied) {
                    applyBtn.classList.add('d-none');
                    alreadyAppliedBadge.classList.remove('d-none');
                } else {
                    applyBtn.classList.remove('d-none');
                    alreadyAppliedBadge.classList.add('d-none');
                    applyBtn.onclick = () => {
                        oppModal.hide();
                        openApplicationModal(data);
                    };
                }

                oppModal.show();
            } catch (err) {
                console.error(err);
                alert('Could not load opportunity details. Please try again.');
            }
        });
    });
}

function openApplicationModal(data) {
    const appModalEl = document.getElementById('applicationFormModal');
    if (!appModalEl) return;
    const appModal = new bootstrap.Modal(appModalEl);

    document.getElementById('applyModalOppTitle').textContent = data.title;
    document.getElementById('applyModalCompany').textContent = data.company_name;
    document.getElementById('applyForm').action = `/student/applications/apply/${data.id}`;

    // Stored resume preview
    const storedResumeRadio = document.getElementById('resumeChoiceStored');
    const storedResumeText = document.getElementById('storedResumeLabel');
    if (data.has_stored_resume) {
        storedResumeRadio.disabled = false;
        storedResumeRadio.checked = true;
        storedResumeText.textContent = `Use verified stored profile resume (${data.stored_resume_path.split('/').pop()})`;
    } else {
        storedResumeRadio.disabled = true;
        document.getElementById('resumeChoiceNew').checked = true;
        storedResumeText.textContent = `No stored resume on file. Please upload a PDF below.`;
    }

    // Render application questions
    const qContainer = document.getElementById('applyModalQuestionsContainer');
    qContainer.innerHTML = '';
    if (data.application_questions && data.application_questions.length > 0) {
        data.application_questions.forEach(q => {
            const grp = document.createElement('div');
            grp.className = 'mb-3';
            grp.innerHTML = `
                <label class="form-label small fw-semibold">
                    ${q.question_text} ${q.is_required ? '<span class="text-danger">*</span>' : '<span class="text-muted">(Optional)</span>'}
                </label>
                <textarea class="form-control form-control-sm" name="question_${q.id}" rows="2" ${q.is_required ? 'required' : ''} maxlength="500"></textarea>
            `;
            qContainer.appendChild(grp);
        });
    } else {
        qContainer.innerHTML = '<p class="text-muted small">No additional screening questions required by this partner.</p>';
    }

    appModal.show();
}

function initCandidateModals() {
    const candModalEl = document.getElementById('candidateProfileModal');
    if (!candModalEl) return;
    const candModal = new bootstrap.Modal(candModalEl);

    document.querySelectorAll('.btn-view-candidate').forEach(btn => {
        btn.addEventListener('click', async () => {
            const studentId = btn.dataset.studentId;
            const oppId = btn.dataset.oppId || '';

            try {
                const res = await fetch(`/industry/api/candidate/${studentId}?opp_id=${oppId}`);
                if (!res.ok) throw new Error('Failed to load candidate');
                const data = await res.json();

                document.getElementById('candModalName').textContent = data.name_display;
                document.getElementById('candModalCollege').textContent = `${data.college} · ${data.branch} (${data.year})`;
                document.getElementById('candModalCGPA').textContent = `CGPA: ${data.cgpa} / 4.0`;
                document.getElementById('candModalGoal').textContent = `Career Target: ${data.career_goal}`;
                document.getElementById('candModalBio').textContent = data.bio || 'No bio provided.';

                // Compatibility
                const compContainer = document.getElementById('candModalCompatibilityContainer');
                if (data.compatibility !== null) {
                    compContainer.classList.remove('d-none');
                    document.getElementById('candModalCompScore').textContent = `${data.compatibility}% Match`;
                } else {
                    compContainer.classList.add('d-none');
                }

                // Verified Skills
                const skillsList = document.getElementById('candModalSkills');
                skillsList.innerHTML = '';
                data.skills.forEach(s => {
                    const badge = document.createElement('span');
                    badge.className = 'badge ' + (s.is_verified ? 'bg-primary' : 'bg-light text-dark border') + ' me-1 mb-1';
                    badge.textContent = `${s.name}: ${s.score !== null ? s.score + '/100 ✓' : 'Not Assessed'}`;
                    skillsList.appendChild(badge);
                });

                // Projects
                const projList = document.getElementById('candModalProjects');
                projList.innerHTML = '';
                if (data.projects && data.projects.length > 0) {
                    data.projects.forEach(p => {
                        const div = document.createElement('div');
                        div.className = 'mb-2 pb-2 border-bottom';
                        div.innerHTML = `
                            <div class="fw-semibold small">${p.title} <span class="text-muted fw-normal">(${p.role})</span></div>
                            <div class="text-muted small">${p.description}</div>
                            <div class="small text-primary mt-1">Tech: ${p.technologies}</div>
                        `;
                        projList.appendChild(div);
                    });
                } else {
                    projList.innerHTML = '<div class="small text-muted">No projects listed yet.</div>';
                }

                candModal.show();
            } catch (err) {
                console.error(err);
                alert('Failed to load candidate profile details.');
            }
        });
    });
}

function initNotificationHandlers() {
    document.querySelectorAll('.btn-mark-read').forEach(btn => {
        btn.addEventListener('click', async () => {
            const notifId = btn.dataset.notifId;
            try {
                const res = await fetch(`/student/notifications/${notifId}/read`, { method: 'POST' });
                if (res.ok) {
                    const item = document.getElementById(`notif-item-${notifId}`);
                    if (item) {
                        item.classList.remove('fw-bold');
                        item.classList.add('opacity-75');
                        btn.remove();
                    }
                }
            } catch (e) {
                console.error(e);
            }
        });
    });
}
