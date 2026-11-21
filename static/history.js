import {
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js";

import { auth } from "./firebase-auth.js";

// Page elements
const historyList = document.getElementById("history-list");
const historyCount = document.getElementById("history-count");
const historyEmpty = document.getElementById("history-empty");

// Show a message in the history area
function showMessage(message) {
    historyList.textContent = "";

    const div = document.createElement("div");
    div.className = "empty-state";
    div.textContent = message;

    historyList.appendChild(div);
}

// Format the timestamp
function formatHistoryDate(value) {
    if (!value) return "Date unavailable";

    // SQLite CURRENT_TIMESTAMP uses UTC.
    const date = new Date(value.replace(" ", "T") + "Z");

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

// Render one history item
function createHistoryCard(item) {
    const card = document.createElement("article");
    card.className = "article-card";

    const title = document.createElement("a");
    title.className = "article-title";
    title.textContent = `arXiv:${item.arxiv_id}`;
    title.href = `https://arxiv.org/abs/${encodeURI(item.arxiv_id)}`;
    title.target = "_blank";
    title.rel = "noopener noreferrer";

    const viewedAt = document.createElement("p");
    viewedAt.className = "article-authors";
    viewedAt.textContent =
        `Viewed on ${formatHistoryDate(item.viewed_at)}`;

    const actions = document.createElement("div");
    actions.className = "article-actions";

    const viewLink = document.createElement("a");
    viewLink.href = title.href;
    viewLink.target = "_blank";
    viewLink.rel = "noopener noreferrer";
    viewLink.textContent = "View on arXiv ↗";

    actions.appendChild(viewLink);

    card.appendChild(title);
    card.appendChild(viewedAt);
    card.appendChild(actions);

    return card;
}

// Load current user's reading history
async function loadReadingHistory(user) {
    historyList.textContent = "";
    historyCount.textContent = "Loading...";

    try {
        // Get a Firebase ID token
        const token = await user.getIdToken();

        // Request data from FastAPI
        const response = await fetch("/history", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(
                `Failed to load history (${response.status})`
            );
        }

        const data = await response.json();
        const history = data.history || [];

        historyList.textContent = "";

        // No history
        if (history.length === 0) {
            historyEmpty.hidden = false;
            historyCount.textContent = "0 articles";
            return;
        }

        historyEmpty.hidden = true;

        // Render history records
        history.forEach(item => {
            historyList.appendChild(createHistoryCard(item));
        });

        historyCount.textContent =
            `${history.length} history records`;

    } catch (error) {
        console.error("Reading history error:", error);

        historyCount.textContent = "Unavailable";
        showMessage(
            "Unable to load reading history. Please try again."
        );
    }
}

// Wait until Firebase restores the login state
onAuthStateChanged(auth, (user) => {
    if (user) {
        historyEmpty.hidden = true;
        loadReadingHistory(user);
    } else {
        historyEmpty.hidden = true;
        historyCount.textContent = "Login required";

        showMessage(
            "Please log in to view your reading history."
        );
    }
});
