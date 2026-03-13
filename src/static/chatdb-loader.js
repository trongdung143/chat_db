(function () {

    if (window.chatdbWidgetLoaded) return;
    window.chatdbWidgetLoaded = true;

    function initChatWidget() {

        const scriptSrc =
            document.currentScript?.src ||
            [...document.getElementsByTagName("script")]
                .map(s => s.src)
                .find(src => src.includes("chat.js"));

        const queryUrl = new URL("/static/query.html", scriptSrc).href;

        // Generate or get client ID
        function getOrGenerateClientId() {
            const storageKey = 'chatdb_client_id';
            let clientId = localStorage.getItem(storageKey);
            if (!clientId) {
                clientId = 'client_' + crypto.randomUUID();
                localStorage.setItem(storageKey, clientId);
            }
            return clientId;
        }

        const clientId = getOrGenerateClientId();
        const queryUrlWithClientId = queryUrl + '?client_id=' + encodeURIComponent(clientId);

        // Gọi API /clear để xóa session
        function clearSession() {
            const clearUrl = baseUrl + "/clear?client_id=" + encodeURIComponent(clientId);
            // dùng sendBeacon để đảm bảo gọi được khi reload/close tab
            navigator.sendBeacon(clearUrl);
        }

        const button = document.createElement("div");
        button.innerHTML = "💬";

        Object.assign(button.style, {
            position: "fixed",
            bottom: "20px",
            right: "20px",
            width: "60px",
            height: "60px",
            background: "#00bcd4",
            borderRadius: "50%",
            color: "white",
            fontSize: "26px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            boxShadow: "0 8px 25px rgba(0,0,0,0.3)",
            zIndex: "999999"
        });

        document.body.appendChild(button);

        const box = document.createElement("div");

        Object.assign(box.style, {
            position: "fixed",
            bottom: "90px",
            right: "20px",
            width: "400px",
            height: "600px",
            background: "white",
            borderRadius: "12px",
            overflow: "hidden",
            boxShadow: "0 10px 35px rgba(0,0,0,0.35)",
            display: "none",
            zIndex: "999999"
        });

        const iframe = document.createElement("iframe");

        iframe.src = queryUrlWithClientId;
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.border = "none";

        box.appendChild(iframe);
        document.body.appendChild(box);

        button.onclick = () => {
            box.style.display = box.style.display === "none" ? "block" : "none";
        };

        // Listen for messages from iframe
        window.addEventListener('message', (event) => {
            if (event.data && event.data.action === 'closeWidget') {
                box.style.display = 'none';
                clearSession(); // gọi /clear khi nhấn nút đóng trong iframe
            }
        });

        // Gọi /clear khi user reload hoặc đóng tab
        window.addEventListener('beforeunload', () => {
            clearSession();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initChatWidget);
    } else {
        initChatWidget();
    }

})();