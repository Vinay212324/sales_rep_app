function getCurrentDate() {
            let today = new Date();
            let options = { year: 'numeric', month: 'long', day: 'numeric' };
            let formattedDate = today.toLocaleDateString('en-US', options);

            document.getElementById("currentDate").innerText = "Date: " + formattedDate;
        };

        // Call function on page load
        getCurrentDate();
function customer_form(){
    window.location.href = "/customers_form";
};






document.addEventListener("DOMContentLoaded", function () {
    async function tokenValid() {
        let base_url = localStorage.getItem("base_url");
        if (!base_url) {
            console.error("⚠️ Base URL not found in localStorage.");
            redirectToLogin();
            return;
        }

        let url = base_url + "/token_validation";
        let token = localStorage.getItem("api_key");
        console.log(token);
        if (!token) {
            console.error("⚠️ API key not found in localStorage.");
            redirectToLogin();
            return;
        }

        let payload = {
            jsonrpc: "2.0",
            method: "call",
            params: { "token": token },
            id: 1 // Change to 1 for debugging
        };

        try {
            let response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            console.log("📡 Fetch response:", response);

            if (!response.ok) {
                console.error("❌ Server error:", response.status, response.statusText);
                alert("Server error: " + response.statusText);
                redirectToLogin();
                return;
            }

            let jsonData = await response.json();
            console.log("📥 API Response:", jsonData);

            if (jsonData.result && jsonData.result.success === true) {
                console.log("✅ Valid token:", jsonData.result.message);

                let storedLogin = localStorage.getItem("login");
                let responseLogin = jsonData.result.user_login.user_login; // Corrected path

                if (storedLogin === responseLogin) {
                    console.log("✅ User login matches. Staying on the page.");
                } else {
                    console.warn("⚠️ User login does not match. Redirecting...");
                    redirectToLogin();
                }
            } else {
                console.warn("❌ Token validation failed.");
                alert("Invalid token. Please log in again.");
                redirectToLogin();
            }
        } catch (error) {
            console.error("⚠️ Network Error:", error.message);
            alert("Network error: " + error.message);
            redirectToLogin();
        }
    }

    function redirectToLogin() {
        window.location.href = "/lin";
    }

    tokenValid();
});

