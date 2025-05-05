// Global değişkenler
let userId = localStorage.getItem('feynmanChatUserId');
let sessionId = localStorage.getItem('feynmanChatSessionId');
let currentCharacter = '';
let isConversationActive = false;

// DOM elementleri
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");
const chatBox = document.getElementById("chatbox");

// Karakter isimleri ve görünen adları
const characterNames = {
  'cocuk': 'Çocuk',
  'universiteli': 'Üniversiteli',
  'hoca': 'Profesör'
};

// Oturum ID'si oluştur (eğer yoksa)
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem('feynmanChatSessionId', sessionId);
}

// Konuşmayı sonlandır fonksiyonu
function endConversation() {
  isConversationActive = false;
  document.querySelector(".chat-container").classList.add("conversation-ended");
  messageInput.disabled = true;
  sendBtn.disabled = true;
}

// Konuşmayı aktifleştir fonksiyonu
function enableConversation() {
  isConversationActive = true;
  document.querySelector(".chat-container").classList.remove("conversation-ended");

  if (messageInput && sendBtn) {
    messageInput.disabled = false;
    sendBtn.disabled = false;
  }
}

// Önceki oturumu yükle
async function loadPreviousSession(sessionId) {
  const chatBox = document.getElementById("chatbox");
  chatBox.innerHTML = `<div class="system-message"><div class="message-content">Önceki konuşma yükleniyor...</div></div>`;

  try {
    const res = await fetch(`/chat-messages/${userId}/${sessionId}`);
    const data = await res.json();

    if (!data.messages || data.messages.length === 0) {
      chatBox.innerHTML = `<div class="system-message"><div class="message-content">Bu oturuma ait mesaj bulunamadı.</div></div>`;
      return;
    }

    // İlk mesajdan karakteri belirle
    currentCharacter = data.messages.find(msg => msg.role !== "system")?.character;
    if (currentCharacter) {
      document.getElementById("current-character").textContent = characterNames[currentCharacter];
    }

    chatBox.innerHTML = ''; // Mevcut içeriği temizle
    
    data.messages.forEach(msg => {
      if (msg.role === "system") return; // Sistem mesajlarını gösterme
      
      const messageEl = document.createElement("div");
      messageEl.className = `message ${msg.role === "user" ? "user-message" : "ai-message"}`;
      
      if (msg.role !== "user") {
        messageEl.setAttribute("data-character", msg.character);
      }

      messageEl.innerHTML = `
        <div class="message-header">${msg.role === "user" ? "Sen" : characterNames[msg.character]}</div>
        <div class="message-content">${msg.content}</div>
      `;
      chatBox.appendChild(messageEl);
    });

    chatBox.scrollTop = chatBox.scrollHeight;
    isConversationActive = true;
    enableConversation();
  } catch (err) {
    chatBox.innerHTML = `<div class="error-message">Mesajlar getirilemedi: ${err.message}</div>`;
  }
}

// Konuşma geçmişini yükle
async function loadChatHistory() {
  if (!userId) return;
  
  const sidebar = document.getElementById("historySidebar");
  const listEl = sidebar.querySelector(".chat-history-list");
  listEl.innerHTML = `<div class="loading">Yükleniyor...</div>`;

  try {
    const res = await fetch(`/chat-history/${userId}`);
    const data = await res.json();

    listEl.innerHTML = "";

    data.sessions.forEach(session => {
      const item = document.createElement("div");
      item.className = "chat-history-item";
      item.textContent = `${session.character} — ${session.first_message.slice(0, 40)}...`;
      item.onclick = async () => {
        sessionId = session.session_id;
        localStorage.setItem("feynmanChatSessionId", sessionId);
        await loadPreviousSession(sessionId);
      };
      listEl.appendChild(item);
    });

    if (data.sessions.length === 0) {
      listEl.innerHTML = "<div style='color: #888;'>Henüz konuşma geçmişiniz yok.</div>";
    }
  } catch (err) {
    listEl.innerHTML = `<div class="error">Geçmiş yüklenemedi: ${err.message}</div>`;
  }
}

// Sayfa yüklendiğinde
document.addEventListener("DOMContentLoaded", () => {
  const characterCards = document.querySelectorAll(".character-card");
  const currentCharacterDisplay = document.getElementById("current-character");
  const endConversationBtn = document.getElementById("end-conversation");
  
  // Loading göstergesi oluştur
  const loadingIndicator = document.createElement("div");
  loadingIndicator.className = "loading-indicator";
  loadingIndicator.innerHTML = "Düşünüyor...";
  loadingIndicator.style.display = "none";
  loadingIndicator.style.color = "#666";
  loadingIndicator.style.fontStyle = "italic";
  loadingIndicator.style.margin = "10px 0";
  document.querySelector(".chat-container").appendChild(loadingIndicator);
  
  // Karakterlerin tıklanma olayları
  characterCards.forEach(card => {
    card.addEventListener("click", () => {
      if (isConversationActive) {
        // Aktif konuşma varsa onay iste
        if (!confirm("Başka bir karaktere geçmek mevcut konuşmayı sonlandıracaktır. Devam etmek istiyor musunuz?")) {
          return;
        }
      }
      
      // Mevcut seçili kartı temizle
      document.querySelectorAll(".character-card.active").forEach(c => {
        c.classList.remove("active");
      });
      
      // Yeni kartı seç
      card.classList.add("active");
      
      // Karakteri ayarla
      currentCharacter = card.getAttribute("data-character");
      currentCharacterDisplay.textContent = characterNames[currentCharacter] || currentCharacter;
      
      // Yeni oturum ID'si oluştur
      sessionId = crypto.randomUUID();
      localStorage.setItem('feynmanChatSessionId', sessionId);
      
      // Konuşmayı aktifleştir
      isConversationActive = true;
      enableConversation();
      
      // Chatbox'ı temizle ve karşılama mesajı ekle
      chatBox.innerHTML = `
        <div class="system-message">
          <div class="message-content">
            ${characterNames[currentCharacter]} ile yeni bir konuşma başlatıldı.
          </div>
        </div>
      `;
      
      // Input'a odaklan
      messageInput.focus();
    });
  });
  
  // Enter tuşu ile mesaj gönderme
  messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendBtn.click();
    }
  });

  // Mesaj gönderme
  sendBtn.addEventListener("click", async () => {
    // Karakter seçilmemiş veya konuşma sonlandırılmışsa işlem yapma
    if (!currentCharacter || !isConversationActive) {
      alert("Lütfen önce bir karakter seçin veya yeni bir konuşma başlatın.");
      return;
    }
    
    const message = messageInput.value.trim();
    if (!message) return;

    // Gönderme butonu devre dışı bırak
    sendBtn.disabled = true;
    
    // Ekrana kullanıcı mesajını ekle
    chatBox.innerHTML += `
      <div class="message user-message">
        <div class="message-header">Sen</div>
        <div class="message-content">${message}</div>
      </div>
    `;
    
    // Input'u temizle ve scroll
    messageInput.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Loading göster
    loadingIndicator.style.display = "block";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Mesajı backend'e gönder
    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: parseInt(userId),
          session_id: sessionId,
          character: currentCharacter,
          message
        })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP hata! Durum: ${res.status}`);
      }

      const data = await res.json();

      // Loading gizle
      loadingIndicator.style.display = "none";

      // Gelen cevabı ekrana ekle
      chatBox.innerHTML += `
        <div class="message ai-message" data-character="${currentCharacter}">
          <div class="message-header">${characterNames[currentCharacter]}</div>
          <div class="message-content">${data.reply}</div>
        </div>
      `;
      
      chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
      // Hata durumunda
      loadingIndicator.style.display = "none";
      chatBox.innerHTML += `
        <div class="message error-message">
          <div class="message-header">Hata</div>
          <div class="message-content">Sunucu hatası: ${err.message}</div>
        </div>
      `;
      chatBox.scrollTop = chatBox.scrollHeight;
    } finally {
      // Gönderme butonu tekrar aktif et
      sendBtn.disabled = false;
    }
  });
  
  // Konuşmayı sonlandır butonu
  endConversationBtn.addEventListener("click", () => {
    // Eğer konuşma zaten sonlandırılmışsa veya hiç başlamadıysa bir şey yapma
    if (!isConversationActive) return;
    
    // Konuşmayı sonlandır
    endConversation();
    
    // Konuşma sonlandırma mesajı
    chatBox.innerHTML += `
      <div class="system-message">
        <div class="message-content">
          Konuşma sonlandırıldı. Yeni bir konuşma başlatmak için karakter seçin.
        </div>
      </div>
      <button class="new-conversation-btn">Yeni Konuşma Başlat</button>
    `;
    
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Yeni konuşma butonu işlevi
    document.querySelector(".new-conversation-btn").addEventListener("click", () => {
      // Aktif karakterle yeni konuşma başlat
      if (currentCharacter) {
        // Yeni oturum ID'si oluştur
        sessionId = crypto.randomUUID();
        localStorage.setItem('feynmanChatSessionId', sessionId);
        
        // Konuşmayı aktifleştir
        enableConversation();
        
        // Chatbox'ı temizle ve karşılama mesajı ekle
        chatBox.innerHTML = `
          <div class="system-message">
            <div class="message-content">
              ${characterNames[currentCharacter]} ile yeni bir konuşma başlatıldı.
            </div>
          </div>
        `;
        
        // Input'a odaklan
        messageInput.focus();
      } else {
        alert("Lütfen önce bir karakter seçin.");
      }
    });
  });

  // Konuşma geçmişi butonuna tıklama olayı
  const historyBtn = document.getElementById("historyBtn");
  if (historyBtn) {
    historyBtn.addEventListener("click", () => {
      loadChatHistory();
      document.getElementById("historySidebar").classList.toggle("open");
    });
  }

  // Önceki oturumu yükle (eğer var ise)
  if (sessionId && userId) {
    setTimeout(() => {
      loadPreviousSession(sessionId);
    }, 300); // DOM tamamen oturduktan sonra çalışsın diye
  }
});