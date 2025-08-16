document.addEventListener("DOMContentLoaded", () => {
  const errorDiv = document.querySelector(".alert.alert-danger");
  if (!errorDiv) return;

  const inputs = document.querySelectorAll(
    'input[name="username"], input[name="password"]'
  );

  inputs.forEach((input) => {
    input.addEventListener("input", () => {
      errorDiv.style.display = "none";

      const invalidFeedbacks = document.querySelectorAll(
        ".invalid-feedback.d-block"
      );
      invalidFeedbacks.forEach((el) => (el.style.display = "none"));
    });
  });
});
