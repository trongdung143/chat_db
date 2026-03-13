(function () {

    // tránh load widget nhiều lần
    if (window.chatdbWidgetLoaded) return;
    window.chatdbWidgetLoaded = true;

    function initChatWidget() {

        // tìm script đang chạy
        const scriptElement =
            document.currentScript ||
            [...document.scripts].find(s => s.src && s.src.includes("chatdb-loader"));

        if (!scriptElement) {
            console.error("ChatDB: cannot detect loader script");
            return;
        }

        const scriptSrc = scriptElement.src;

        // domain của server widget
        const baseUrl = new URL(scriptSrc).origin;

        // url iframe chat
        const queryUrl = new URL("/static/query.html", baseUrl).href;

        // ===== client id =====
        function getOrGenerateClientId() {
            const storageKey = "chatdb_client_id";
            let clientId = localStorage.getItem(storageKey);

            if (!clientId) {
                clientId = "client_" + crypto.randomUUID();
                localStorage.setItem(storageKey, clientId);
            }

            return clientId;
        }

        const clientId = getOrGenerateClientId();

        const iframeUrl =
            queryUrl + "?client_id=" + encodeURIComponent(clientId);

        // ===== clear session =====
        function clearSession() {
            const clearUrl =
                baseUrl + "/clear?client_id=" + encodeURIComponent(clientId);

            try {
                navigator.sendBeacon(clearUrl);
            } catch (e) {
                fetch(clearUrl).catch(() => { });
            }
        }

        // ===== chat button =====
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

        // ===== chat box =====
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

        // ===== iframe =====
        const iframe = document.createElement("iframe");

        iframe.src = iframeUrl;
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.border = "none";

        box.appendChild(iframe);
        document.body.appendChild(box);

        // ===== toggle widget =====
        button.onclick = () => {
            box.style.display =
                box.style.display === "none" ? "block" : "none";
        };

        // ===== listen message từ iframe =====
        window.addEventListener("message", (event) => {

            if (!event.data) return;

            if (event.data.action === "closeWidget") {
                box.style.display = "none";
                clearSession();
            }

        });

        // ===== clear khi reload / close =====
        window.addEventListener("beforeunload", () => {
            clearSession();
        });

        // debug
        console.log("ChatDB widget loaded");
        console.log("script:", scriptSrc);
        console.log("iframe:", iframeUrl);
        console.log("api:", baseUrl);

    }

    // đảm bảo DOM đã sẵn sàng
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initChatWidget);
    } else {
        initChatWidget();
    }

})();