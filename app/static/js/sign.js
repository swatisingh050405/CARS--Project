document.getElementById("signup-form").addEventListener("submit", function (e) {
  e.preventDefault();

  const inputs = this.querySelectorAll("input");
  const name = inputs[0].value.trim();
  const email = inputs[1].value.trim();
  const password = inputs[2].value;
  const confirmPassword = inputs[3].value;

  if (!name || !email || !password || !confirmPassword) {
    alert("Please fill out all fields.");
    return;
  }

  if (password !== confirmPassword) {
    alert("Passwords do not match.");
    return;
  }

  // Simulate saving user info (replace with real backend logic later)
  localStorage.setItem("user", email);
  alert("Signup successful! Redirecting to dashboard...");
  window.location.href = "dashboard.html";
});
