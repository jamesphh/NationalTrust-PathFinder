// Performs form validation on a registration form.
function validateForm() {

  // Retrieve values of the username and password fields from the form
  var username = document.forms["registerForm"]["username"].value;
  var password = document.forms["registerForm"]["password"].value;

  // Get references to the elements where error messages will be displayed
  var usernameError = document.getElementById("usernameError");
  var passwordError = document.getElementById("passwordError");

  // Clear any previous error messages
  usernameError.innerText = "";
  passwordError.innerText = "";

  // Sets isValid to true
  var isValid = true;

  // Checks if the username length is less than or equal to 5 or greater than or equal to 12
  if (username.length <= 5 || username.length >= 12) {
    // Display an error message in the username error message element
    usernameError.innerHTML = "Username must be between 5 and 12 characters long";
    isValid = false;
  }

  // Checks if the username contains only letters, numbers, and underscores
  if (!username.match(/^[a-zA-Z0-9_]+$/)) {
    // Display an error message in the username error message element
    usernameError.innerHTML = "Username can only contain letters, numbers, and underscores";
    isValid = false;
  }

  // Checks if the password contains at least one capital letter, one number, and one special character
  var hasCapital = false;
  var hasNumber = false;
  var hasSpecial = false;
  var specialChars = "!@#$%^&+=";

  // Loop through each character in the password
  for (var i = 0; i < password.length; i++) {
    var char = password.charAt(i);
    // Checks if the character is a capital letter
    if (char >= 'A' && char <= 'Z') {
      hasCapital = true;
    } 
    // Checks if the character is a number
    else if (char >= '0' && char <= '9') {
      hasNumber = true;
    } 
    // Checks if the character is a special character
    else if (specialChars.indexOf(char) != -1) {
      hasSpecial = true;
    }
  }

  // If the password does not contain at least one capital letter, one number, and one special character
  if (!hasCapital || !hasNumber || !hasSpecial) {
    // Display an error message in the password error message element
    passwordError.innerHTML = "Password must contain at least one capital letter, number, and special character";
    // Set isValid to false
    isValid = false;
  }

  // Checks if the password length is less than 6
  if (password.length < 6) {
    // Display an error message in the password error message element
    passwordError.innerHTML = "Password must be at least 6 characters long";
    // Set isValid to false
    isValid = false;
  }
  
  // Return the boolean value of isValid
  return isValid;
}
