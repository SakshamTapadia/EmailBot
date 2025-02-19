document.addEventListener('DOMContentLoaded', function() {
    // File upload preview
    const fileInput = document.getElementById('recipient-file');
    const fileLabel = document.querySelector('.custom-file-label');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'Choose file';
            fileLabel.textContent = fileName;
        });
    }

    // Scheduling options
    const sendNowRadio = document.getElementById('send-now');
    const sendLaterRadio = document.getElementById('send-later');
    const scheduleInputs = document.querySelector('.schedule-inputs');

    if (sendNowRadio && sendLaterRadio) {
        sendNowRadio.addEventListener('change', function() {
            scheduleInputs.style.display = 'none';
            document.getElementById('schedule-date').required = false;
            document.getElementById('schedule-time').required = false;
        });

        sendLaterRadio.addEventListener('change', function() {
            scheduleInputs.style.display = 'block';
            document.getElementById('schedule-date').required = true;
            document.getElementById('schedule-time').required = true;
        });
    }

    // Email content preview
    const previewBtn = document.getElementById('preview-btn');
    if (previewBtn) {
        previewBtn.addEventListener('click', function(e) {
            const content = document.getElementById('content').value;
            const subject = document.getElementById('subject').value;

            if (!content || !subject) {
                alert('Please fill in both subject and content');
                e.preventDefault();
                return false;
            }

            // Validate scheduling if "Send Later" is selected
            if (sendLaterRadio.checked) {
                const scheduleDate = document.getElementById('schedule-date').value;
                const scheduleTime = document.getElementById('schedule-time').value;

                if (!scheduleDate || !scheduleTime) {
                    alert('Please select both date and time for scheduled sending');
                    e.preventDefault();
                    return false;
                }

                // Check if selected datetime is in the future
                const scheduledDateTime = new Date(scheduleDate + ' ' + scheduleTime);
                if (scheduledDateTime <= new Date()) {
                    alert('Please select a future date and time');
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    // Form validation
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', function(e) {
            const subject = document.getElementById('subject').value;
            const content = document.getElementById('content').value;

            if (!subject || !content) {
                e.preventDefault();
                alert('Please fill in all required fields');
                return false;
            }
        });
    }

    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 100);
    });
});