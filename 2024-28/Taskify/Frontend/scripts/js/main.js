// Taskify Frontend JavaScript
document.addEventListener("DOMContentLoaded", () => {
  console.log("Taskify frontend loaded.");

  // Auto-dismiss flash messages
  initFlashMessages();

  // Add form validation enhancements
  initFormValidation();

  // Add smooth scrolling for better UX
  initSmoothScrolling();
});

// Flash message functionality
function initFlashMessages() {
  const flashMessages = document.querySelectorAll(".flash-message");

  flashMessages.forEach((message) => {
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      message.style.animation = "slideOut 0.3s ease-in";
      setTimeout(() => {
        message.remove();
      }, 300);
    }, 5000);

    // Add click to dismiss
    message.addEventListener("click", () => {
      message.style.animation = "slideOut 0.3s ease-in";
      setTimeout(() => {
        message.remove();
      }, 300);
    });
  });
}

// Form validation enhancements
function initFormValidation() {
  const forms = document.querySelectorAll(".auth-form");

  forms.forEach((form) => {
    const inputs = form.querySelectorAll("input[required]");
    const submitButton = form.querySelector('button[type="submit"]');

    inputs.forEach((input) => {
      // Add real-time validation feedback
      input.addEventListener("blur", () => {
        validateInput(input);
      });

      input.addEventListener("input", () => {
        clearInputError(input);
        // Re-enable submit button if all fields are valid
        if (submitButton) {
          submitButton.disabled = false;
        }
      });
    });

    // Prevent form submission if validation fails
    form.addEventListener("submit", (e) => {
      let isValid = true;

      inputs.forEach((input) => {
        if (!validateInput(input)) {
          isValid = false;
        }
      });

      if (!isValid) {
        e.preventDefault();
        showFormError("Please fix the errors above before submitting.");
      } else if (submitButton) {
        // Show loading state
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";
      }
    });
  });
}

// Validate individual input
function validateInput(input) {
  const value = input.value.trim();
  const type = input.type;
  const name = input.name;

  clearInputError(input);

  if (!value) {
    showInputError(input, "This field is required");
    return false;
  }

  if (name === "username") {
    if (value.length < 5 || value.length > 20) {
      showInputError(input, "Username must be between 5 and 20 characters");
      return false;
    }
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      showInputError(input, "Username can only contain letters, numbers, and underscores");
      return false;
    }
  }

  if (name === "password") {
    if (value.length < 8) {
      showInputError(input, "Password must be at least 8 characters long");
      return false;
    }
    if (!/(?=.*[a-z])/.test(value)) {
      showInputError(input, "Password must contain at least one lowercase letter");
      return false;
    }
    if (!/(?=.*[A-Z])/.test(value)) {
      showInputError(input, "Password must contain at least one uppercase letter");
      return false;
    }
    if (!/(?=.*\d)/.test(value)) {
      showInputError(input, "Password must contain at least one number");
      return false;
    }
    if (!/(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/.test(value)) {
      showInputError(input, "Password must contain at least one special character");
      return false;
    }
  }

  if (name === "confirm_password") {
    const password = document.querySelector('input[name="password"]');
    if (password && value !== password.value) {
      showInputError(input, "Passwords do not match");
      return false;
    }
  }

  return true;
}

// Show input error
function showInputError(input, message) {
  input.style.borderColor = "#ef4444";
  input.style.boxShadow = "0 0 8px rgba(239, 68, 68, 0.5)";

  // Remove existing error message
  const existingError = input.parentNode.querySelector(".input-error");
  if (existingError) {
    existingError.remove();
  }

  // Add new error message
  const errorDiv = document.createElement("div");
  errorDiv.className = "input-error";
  errorDiv.style.color = "#ef4444";
  errorDiv.style.fontSize = "0.8rem";
  errorDiv.style.marginTop = "0.3rem";
  errorDiv.textContent = message;

  input.parentNode.appendChild(errorDiv);
}

// Show form-level error
function showFormError(message) {
  // Remove existing form error
  const existingError = document.querySelector(".form-error");
  if (existingError) {
    existingError.remove();
  }

  // Add new form error
  const errorDiv = document.createElement("div");
  errorDiv.className = "form-error";
  errorDiv.style.color = "#ef4444";
  errorDiv.style.fontSize = "0.9rem";
  errorDiv.style.marginBottom = "1rem";
  errorDiv.style.padding = "0.5rem";
  errorDiv.style.backgroundColor = "rgba(239, 68, 68, 0.1)";
  errorDiv.style.border = "1px solid rgba(239, 68, 68, 0.3)";
  errorDiv.style.borderRadius = "8px";
  errorDiv.textContent = message;

  const form = document.querySelector(".auth-form");
  if (form) {
    form.insertBefore(errorDiv, form.firstChild);
  }
}

// Clear input error
function clearInputError(input) {
  input.style.borderColor = "";
  input.style.boxShadow = "";

  const errorDiv = input.parentNode.querySelector(".input-error");
  if (errorDiv) {
    errorDiv.remove();
  }
}

// Email validation helper
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Smooth scrolling for better UX
function initSmoothScrolling() {
  // Add smooth scrolling to all anchor links
  const links = document.querySelectorAll('a[href^="#"]');

  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
}

// Add CSS for slideOut animation
const style = document.createElement("style");
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .input-error {
        animation: fadeIn 0.2s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
