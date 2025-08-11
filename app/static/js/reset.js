
    document.getElementById('reset-form').addEventListener('submit', function (e) {
      e.preventDefault();

      const otp = document.getElementById('otp').value.trim();
      const newPass = document.getElementById('new-password').value;
      const confirmPass = document.getElementById('confirm-password').value;

      if (otp.length !== 6 || isNaN(otp)) {
        alert("Please enter a valid 6-digit OTP.");
        return;
      }

      if (newPass !== confirmPass) {
        alert("Passwords do not match.");
        return;
      }

      // Proceed with password reset API call
      alert("Password reset successful!");
      // window.location.href = "/login.html"; // redirect after success
    });
 