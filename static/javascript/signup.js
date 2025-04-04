  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-analytics.js";
  import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
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

  //initailize authentication
  const auth = getAuth(app);
  
  //submit button for sign up
  const submitsignup= document.getElementById('submitsignup');

  // Add event listener to the button
  submitsignup.addEventListener("click", function(event){
      event.preventDefault()

      //get input values
      const fullname= document.getElementById('fullname').value;
      const email= document.getElementById('email').value;
      const password= document.getElementById('password').value;

      //sign up new users
     createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
      // Signed up 
      const user = userCredential.user;
      alert("creating account...")
      console.log("User signed up:", user);
      window.location.href="/signin"
      // ...
      })
     .catch((error) => {
       const errorCode = error.code;
       const errorMessage = error.message;
       alert(errorMessage)
       // ..
       console.log("Error during signup:", errorCode, errorMessage);
      });
    })

