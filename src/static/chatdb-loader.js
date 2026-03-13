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
            const clearUrl = baseUrl + "/client/v1/clear?client_id=" + encodeURIComponent(id || clientId);
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

        // ===== inject Google Font =====
        const fontLink = document.createElement("link");
        fontLink.rel = "stylesheet";
        fontLink.href = "https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&display=swap";
        document.head.appendChild(fontLink);

        // ===== inject CSS =====
        const style = document.createElement("style");
        style.textContent = `
            #chatdb-widget-btn {
                position: fixed;
                bottom: 24px;
                right: 24px;
                width: 56px;
                height: 56px;
                background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
                border-radius: 18px;
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 6px 24px rgba(37,99,235,0.45), 0 2px 8px rgba(0,0,0,0.12);
                z-index: 999999;
                transition: transform 0.22s cubic-bezier(.34,1.56,.64,1), box-shadow 0.22s ease;
                font-family: 'Sora', sans-serif;
            }
            #chatdb-widget-btn:hover {
                transform: scale(1.1) translateY(-2px);
                box-shadow: 0 12px 32px rgba(37,99,235,0.55), 0 4px 12px rgba(0,0,0,0.14);
            }
            #chatdb-widget-btn img {
                width: 30px;
                height: 30px;
                object-fit: contain;
                transition: transform 0.3s ease;
            }
            #chatdb-widget-btn.open img {
                transform: rotate(90deg) scale(0.85);
            }

            #chatdb-greet-bubble {
                position: fixed;
                bottom: 30px;
                right: 92px;
                background: white;
                border-radius: 14px 14px 4px 14px;
                padding: 9px 15px;
                font-family: 'Sora', sans-serif;
                font-size: 12.5px;
                font-weight: 500;
                color: #0f172a;
                box-shadow: 0 8px 28px rgba(37,99,235,0.14), 0 2px 8px rgba(0,0,0,0.06);
                white-space: nowrap;
                z-index: 999999;
                opacity: 0;
                border: 1px solid #e2e8f8;
                overflow: hidden;
            }
            #chatdb-greet-bubble::after {
                content: '';
                position: absolute;
                right: -7px;
                bottom: 14px;
                border: 6px solid transparent;
                border-left-color: white;
                border-right-width: 0;
            }
            #chatdb-greet-bubble .cursor { display: none; }

            #chatdb-box {
                position: fixed;
                bottom: 94px;
                right: 24px;
                width: 390px;
                height: 590px;
                border-radius: 20px;
                overflow: hidden;
                box-shadow:
                    0 8px 16px rgba(37,99,235,0.08),
                    0 16px 40px rgba(37,99,235,0.14),
                    0 32px 80px rgba(37,99,235,0.18),
                    0 48px 120px rgba(0,0,0,0.12);
                z-index: 999998;
                display: none;
                transform-origin: bottom right;
                animation: chatdb-open 0.3s cubic-bezier(.34,1.3,.64,1) both;
                font-family: 'Sora', sans-serif;
            }
            #chatdb-box.visible {
                display: block;
            }
            @keyframes chatdb-open {
                from { opacity: 0; transform: scale(0.82) translateY(10px); }
                to   { opacity: 1; transform: scale(1) translateY(0); }
            }

            #chatdb-box iframe {
                width: 100%;
                height: 100%;
                border: none;
                display: block;
            }

            @media (max-width: 480px) {
                #chatdb-box {
                    width: 100vw;
                    height: 100dvh;
                    bottom: 0;
                    right: 0;
                    border-radius: 0;
                }
                #chatdb-greet-bubble {
                    display: none;
                }
            }
        `;
        document.head.appendChild(style);

        // ===== greeting bubble với typewriter loop =====
        const greetBubble = document.createElement("div");
        greetBubble.id = "chatdb-greet-bubble";
        document.body.appendChild(greetBubble);

        const greetText = "Xin chào, tôi có thể hỗ trợ gì ?";
        const textSpan = document.createElement("span");
        const cursor = document.createElement("span");
        cursor.classList.add("cursor");
        greetBubble.appendChild(textSpan);
        greetBubble.appendChild(cursor);

        let greetTimer = null;
        let greetRunning = false;

        function stopGreet() {
            greetRunning = false;
            clearTimeout(greetTimer);
            greetTimer = null;
        }

        function startGreet(delay) {
            stopGreet();
            greetRunning = true;
            greetTimer = setTimeout(runGreetLoop, delay || 1000);
        }

        function runGreetLoop() {
            if (!greetRunning) return;
            let i = 0;
            textSpan.textContent = "";
            greetBubble.style.opacity = "1";
            greetBubble.style.transition = "opacity 0.5s ease";

            function type() {
                if (!greetRunning) return;
                if (i < greetText.length) {
                    textSpan.textContent += greetText[i++];
                    greetTimer = setTimeout(type, 45);
                } else {
                    // Đợi 10s rồi fade out
                    greetTimer = setTimeout(() => {
                        if (!greetRunning) return;
                        greetBubble.style.opacity = "0";
                        // Đợi 5s rồi lặp lại
                        greetTimer = setTimeout(() => {
                            if (!greetRunning) return;
                            runGreetLoop();
                        }, 5000);
                    }, 10000);
                }
            }
            type();
        }

        // Bắt đầu sau 1s
        startGreet(1000);

        // ===== chat button =====
        const button = document.createElement("button");
        button.id = "chatdb-widget-btn";
        button.setAttribute("aria-label", "Mở chat hỗ trợ");
        button.innerHTML = `<img src="https://cdn.officeai.vn/file/ai-agent-icon.png" alt="Chat" />`;
        document.body.appendChild(button);

        // ===== chat box =====
        const box = document.createElement("div");
        box.id = "chatdb-box";

        // ===== iframe =====
        const iframe = document.createElement("iframe");
        iframe.src = buildIframeUrl(clientId);
        iframe.allow = "clipboard-write";
        iframe.setAttribute("aria-label", "Chatbot CRM");

        box.appendChild(iframe);
        document.body.appendChild(box);

        // ===== toggle open/close =====
        let isOpen = false;

        button.onclick = () => {
            isOpen = !isOpen;
            if (isOpen) {
                box.classList.add("visible");
                box.style.animation = "none";
                requestAnimationFrame(() => { box.style.animation = ""; });
                stopGreet();
                greetBubble.style.display = "none";
                button.classList.add("open");
            } else {
                box.classList.remove("visible");
                button.classList.remove("open");
                greetBubble.style.display = "";
                startGreet(1500);
            }
        };

        // ===== listen message từ iframe (✕ button) =====
        // Khi nhấn ✕: clear session cũ → tạo session mới → reload iframe
        window.addEventListener("message", async (event) => {
            if (!event.data) return;

            if (event.data.action === "closeWidget") {
                box.classList.remove("visible");
                button.classList.remove("open");
                isOpen = false;

                // Khởi động lại loop greeting
                greetBubble.style.display = "";
                startGreet(1500);

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