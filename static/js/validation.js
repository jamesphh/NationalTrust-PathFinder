function validateForm() {
  const form = document.forms["registerForm"];
  const username = form["username"].value;
  const password = form["password"].value;

  const usernameError = document.getElementById("usernameError");
  const passwordError = document.getElementById("passwordError");

  usernameError.innerText = "";
  passwordError.innerText = "";

  let isValid = true;

  // Username validation
  if (username.length < 5 || username.length > 12) {
    usernameError.innerText = "Username must be between 5 and 12 characters long";
    isValid = false;
  } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    usernameError.innerText = "Username can only contain letters, numbers, and underscores";
    isValid = false;
  }

  // Password validation: at least 6 chars, 1 uppercase, 1 number, 1 special
  const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&+=]).{6,}$/;
  if (!passwordRegex.test(password)) {
    passwordError.innerText = "Password must be at least 6 characters and contain a capital letter, number, and special character";
    isValid = false;
  }

  return isValid;
}
