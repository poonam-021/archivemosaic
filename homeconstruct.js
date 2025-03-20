document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("authModal");
    const openModalBtn = document.getElementById("openModal");
    const closeModalBtn = document.getElementById("closeModal");
  
    // Open modal on button click
    openModalBtn.addEventListener("click", function () {
      modal.style.display = "flex";
    });
  
    // Close modal on close button click
    closeModalBtn.addEventListener("click", function () {
      modal.style.display = "none";
    });
  
    // Close modal when clicking outside of it
    window.addEventListener("click", function (event) {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    });
  });