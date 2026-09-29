// AI Project Interview Trainer - Interactive Client Scripts

document.addEventListener("DOMContentLoaded", function () {
  // 1. Autofill Sample Project Button
  const fillSampleBtn = document.getElementById("btn-fill-sample");
  if (fillSampleBtn) {
    fillSampleBtn.addEventListener("click", async function () {
      fillSampleBtn.disabled = true;
      const originalText = fillSampleBtn.innerHTML;
      fillSampleBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Loading Sample...';

      try {
        const response = await fetch("/api/sample-project");
        if (!response.ok) throw new Error("Failed to load sample project.");
        const data = await response.json();

        // Populate fields
        for (const [key, value] of Object.entries(data)) {
          const field = document.getElementById(`field-${key}`) || document.querySelector(`[name="${key}"]`);
          if (field) {
            field.value = value;
            // Briefly highlight filled field
            field.classList.add("bg-warning-subtle");
            setTimeout(() => field.classList.remove("bg-warning-subtle"), 1000);
          }
        }
      } catch (err) {
        console.error("Error autofilling sample:", err);
        alert("Could not load sample project. Please fill manually.");
      } finally {
        fillSampleBtn.disabled = false;
        fillSampleBtn.innerHTML = originalText;
      }
    });
  }

  // 2. Character Counters
  const trackedTextareas = document.querySelectorAll("textarea[maxlength]");
  trackedTextareas.forEach(textarea => {
    const max = textarea.getAttribute("maxlength");
    const counter = document.getElementById(`${textarea.id}-count`);
    if (counter && max) {
      textarea.addEventListener("input", () => {
        counter.textContent = `${textarea.value.length} / ${max}`;
      });
    }
  });

  // 3. Interview Submission UI enhancements
  const interviewForm = document.getElementById("mock-interview-form");
  if (interviewForm) {
    const submitBtn = document.getElementById("btn-submit-answer");
    const answerInput = document.getElementById("student-answer-input");

    interviewForm.addEventListener("submit", function () {
      if (answerInput && answerInput.value.trim().length === 0) {
        return; // Let HTML5 validation handle empty
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Evaluating Answer with AI...';
      }
    });
  }

  // 4. Print / PDF Export
  const printBtn = document.getElementById("btn-print-report");
  if (printBtn) {
    printBtn.addEventListener("click", function () {
      window.print();
    });
  }
});
