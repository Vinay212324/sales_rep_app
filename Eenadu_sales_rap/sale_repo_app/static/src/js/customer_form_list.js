document.addEventListener("DOMContentLoaded", function () {

    //filter the get user form list

    let login = document.getElementById('login');
    let unit =document.getElementById('unit');
    let start_date = document.getElementById('start_date');
    let end_date = document.getElementById('end_date'):


    let formData = {
        login: "",
        unit: "",
        start_date: ""
        end_date: ""
    };

//    // Form validation function
//    function validateFormData(formData) {
//        let isValid = true;
//
//        if (!formData.login) {
//            identityer.textContent = "User ID is Required*";
//            isValid = false;
//        } else {
//            identityer.textContent = "";
//        }
//
//        if (!formData.password) {
//            passwordER.textContent = "Password is Required*";
//            isValid = false;
//        } else {
//            passwordER.textContent = "";
//        }
//
//        return isValid;
//    }

    // Function to submit form data
    async function submitFormData(formData) {
        let base_url = localStorage.getItem('base_url');
        let url = base_url + "/web/session/authenticate";

        // Clear previous login from localStorage
        localStorage.setItem("login", formData.login);

        let payload = {
            jsonrpc: "2.0",
            method: "call",
            params: {
                login: formData.login,
                password: formData.password
            },
            id: new Date().getTime()
        };

        let params = {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        };

        try {
            let response = await fetch(url, params);

            if (!response.ok) {
                throw new Error("HTTP error! Status: " + response.status);
            }

            let jsonData = await response.json();
            console.log("API Response:", jsonData); // Debugging log

            if (jsonData.result) {
                console.log("Login successful:", jsonData.result);

                // Extract session ID (since Odoo does not provide API key by default)
                let user_id = jsonData.result.user_id || null;
                let api_key = jsonData.result.api_key || null;

                if (user_id && api_key) {
                    // Store session info in local storage
                    localStorage.setItem("api_key", api_key);
                    localStorage.setItem("user_id", user_id);

                    alert("Login successful!\nUser ID: " + user_id);

                    // Redirect user after login
                    window.location.href = "/dashboard";
                } else {
                    alert("Login failed! No session received.");
                }
            } else if (jsonData.error) {
                console.warn("Login failed:", jsonData.error);
                alert("Invalid credentials: " + jsonData.error.message);
            } else {
                alert("Unexpected response from server. Please try again.");
            }
        } catch (error) {
            console.error("Error during login:", error);
            alert("Network error. Please try again later.");
        }
    }




    // Handle form submission
    myFormEl.addEventListener("submit", function (event) {
        event.preventDefault();

        // Validate before submitting
        if (validateFormData(formData)) {
            submitFormData(formData);
        }
    });

});


