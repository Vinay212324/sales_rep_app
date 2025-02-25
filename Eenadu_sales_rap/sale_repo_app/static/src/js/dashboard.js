function getCurrentDate() {
            let today = new Date();
            let options = { year: 'numeric', month: 'long', day: 'numeric' };
            let formattedDate = today.toLocaleDateString('en-US', options);

            document.getElementById("currentDate").innerText = "Date: " + formattedDate;
        }

        // Call function on page load
        getCurrentDate();
function customer_form(){
    window.location.href = "/customers_form";
}