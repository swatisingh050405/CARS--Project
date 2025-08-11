document.getElementById("login-form").addEventListener("submit", function (e) {
  e.preventDefault();

  const email = this.querySelector("input[type='email']").value;
  const password = this.querySelector("input[type='password']").value;

  if (!email || !password) {
    alert("Please fill out both fields.");
    return;
  }

  // Placeholder authentication logic
  if (email === "admin@example.com" && password === "admin123") {
    localStorage.setItem("user", email); // Store login
    window.location.href = "/dashboard";
  } else {
    alert("Invalid credentials. Try admin@example.com / admin123");
  }
});
