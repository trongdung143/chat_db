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

        let clientId = getOrGenerateClientId();

        function buildIframeUrl(id) {
            return queryUrl + "?client_id=" + encodeURIComponent(id);
        }

        // ===== clear session =====
        function clearSession(id) {
            const clearUrl =
                baseUrl + "/client/v1/clear?client_id=" + encodeURIComponent(id || clientId);

            try {
                navigator.sendBeacon(clearUrl);
            } catch (e) {
                fetch(clearUrl).catch(() => { });
            }
        }

        // ===== register client =====
        async function registerClient(id) {
            try {
                const res = await fetch(baseUrl + "/client/v1/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ client_id: id }),
                });
                const data = await res.json();
                return data.success || (data.message && data.message.includes("tồn tại"));
            } catch (e) {
                return false;
            }
        }

        // ===== check session còn sống không =====
        async function checkClient(id) {
            try {
                const res = await fetch(baseUrl + "/client/v1/check?client_id=" + encodeURIComponent(id));
                const data = await res.json();
                return data.exists === true;
            } catch (e) {
                return false;
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

        iframe.src = buildIframeUrl(clientId);
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.border = "none";

        box.appendChild(iframe);
        document.body.appendChild(box);

        // ===== 💬 chỉ toggle đóng/mở =====
        button.onclick = () => {
            box.style.display = box.style.display === "none" ? "block" : "none";
        };

        // ===== listen message từ iframe (✕ button) =====
        // Khi nhấn ✕: clear session cũ → tạo session mới → reload iframe
        window.addEventListener("message", async (event) => {

            if (!event.data) return;

            if (event.data.action === "closeWidget") {
                box.style.display = "none";

                // Clear session cũ
                clearSession(clientId);

                // Tạo client_id mới để lần mở tiếp là session sạch
                const newId = "client_" + crypto.randomUUID();
                clientId = newId;

                // Chỉ update localStorage sau khi iframe mới đã load
                iframe.onload = () => {
                    localStorage.setItem("chatdb_client_id", newId);
                    iframe.onload = null;
                };

                iframe.src = buildIframeUrl(newId);
            }

        });

        // ===== clear khi reload / close tab =====
        window.addEventListener("beforeunload", () => {
            clearSession();
        });

        // debug
        console.log("ChatDB widget loaded");
        console.log("script:", scriptSrc);
        console.log("iframe:", buildIframeUrl(clientId));
        console.log("api:", baseUrl);

    }

    // đảm bảo DOM đã sẵn sàng
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initChatWidget);
    } else {
        initChatWidget();
    }

})();