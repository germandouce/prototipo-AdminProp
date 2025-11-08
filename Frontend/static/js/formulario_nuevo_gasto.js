document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById("add-expense-btn").addEventListener("click", function () {
        document.getElementById("modal-overlay-expenses").style.display = "block";
    });

    document.getElementById("cancel-expense-btn").addEventListener("click", function () {
        document.getElementById("modal-overlay-expenses").style.display = "none";
    });
});