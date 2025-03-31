// Import necessary Firebase SDK functions
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-analytics.js";
import { getAuth, signInWithEmailAndPassword, sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBHEFkPl68Q1LDYUrEvSVb7o_V7YFUmL9A",
  authDomain: "digital-archive-cultural-data.firebaseapp.com",
  projectId: "digital-archive-cultural-data",
  storageBucket: "digital-archive-cultural-data.firebasestorage.app",
  messagingSenderId: "551249541025",
  appId: "1:551249541025:web:d70e98238df208726dfde0",
  measurementId: "G-BG5G8300DL"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Initialize authentication
const auth = getAuth(app);

// Get elements
const submitSignIn = document.getElementById('submitsignin');
const resetPasswordButton = document.getElementById('reset-password-btn');
const resetPasswordContainer = document.getElementById('reset-password-container');
const resetEmailInput = document.getElementById('reset-email');
const signInEmailInput = document.getElementById('email');

// Sign-In Event Listener
submitSignIn.addEventListener("click", function (event) {
  event.preventDefault();

  // Get input values
  const email = signInEmailInput.value;
  const password = document.getElementById('password').value;

  // Sign in existing users
  signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      // Signed in successfully
      const user = userCredential.user;
      alert("Successfully signed in...");
      console.log("User signed in:", user);

      window.location.href = "/upload"; // Redirect to upload page
    })
    .catch((error) => {
      const errorCode = error.code;
      const errorMessage = error.message;
      alert(`Error: ${errorMessage}`); // Corrected alert to display the error message
      console.log("Error during sign in:", errorCode, errorMessage);
    });
});

// Forgot Password Button Event Listener
resetPasswordButton.addEventListener('click', function () {
  // Get the email entered during sign-in
  const enteredEmail = signInEmailInput.value;

  if (enteredEmail) {
    // Pre-fill the reset email input with the entered email
    resetEmailInput.value = enteredEmail;

    // Show the password reset form
    resetPasswordContainer.style.display = 'block';

    // Send password reset email directly
    sendPasswordResetEmail(auth, enteredEmail)
      .then(() => {
        alert("Password reset email sent! Please check your inbox.");
        resetPasswordContainer.style.display = 'none';  // Hide the form after sending the email
      })
      .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        alert(`Error: ${errorMessage}`); // Show error message
        console.log("Error during password reset:", errorCode, errorMessage);
      });
  } else {
    alert("Please enter your email first.");
  }
});
