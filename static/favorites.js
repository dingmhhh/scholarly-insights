
import {
    onAuthStateChanged,
    signOut
} from "https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js";

import { auth } from "./firebase-auth.js";

// Page elements
const favoritesList = document.getElementById("favorites-list");
const favoritesCount = document.getElementById("favorites-count");
const favoritesEmpty = document.getElementById("favorites-empty");

const loginBtn = document.getElementById("login-btn");
const logoutBtn = document.getElementById("logout-btn");
const userEmail = document.getElementById("user-email");


// Show a message
function showMessage(message) {
    favoritesList.textContent = "";

    const paragraph = document.createElement("p");
    paragraph.textContent = message;

    favoritesList.appendChild(paragraph);
}


// Remove a saved article
async function removeFavorite(articleId) {
    const user = auth.currentUser;

    if (!user) {
        throw new Error("Please log in first.");
    }

    const token = await user.getIdToken();

    const response = await fetch(
        `/favorites/${encodeURIComponent(articleId)}`,
        {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));

        throw new Error(
            data.detail || "Failed to remove favorite"
        );
    }
}


// Create one favorite card
function createFavoriteCard(item) {
    const card = document.createElement("article");
    card.className = "article-card";

    // Article title / arXiv ID
    const title = document.createElement("a");
    title.className = "article-title";
    title.textContent = `arXiv:${item.arxiv_id}`;
    title.href =
        `https://arxiv.org/abs/${encodeURIComponent(item.arxiv_id)}`;
    title.target = "_blank";
    title.rel = "noopener noreferrer";

    // Subtitle
    const description = document.createElement("p");
    description.className = "article-authors";
    description.textContent = "Saved to your research library";

    // Actions
    const actions = document.createElement("div");
    actions.className = "article-actions";

    const viewLink = document.createElement("a");
    viewLink.href = title.href;
    viewLink.target = "_blank";
    viewLink.rel = "noopener noreferrer";
    viewLink.textContent = "View on arXiv ↗";

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "remove-favorite-btn";
    removeBtn.textContent = "♥ Remove";

    removeBtn.addEventListener("click", async () => {
        removeBtn.disabled = true;
        removeBtn.textContent = "Removing...";

        try {
            await removeFavorite(item.arxiv_id);

            // Reload favorites after deletion
            await loadFavorites(auth.currentUser);

        } catch (error) {
            console.error("Remove favorite error:", error);

            alert(error.message);
            removeBtn.disabled = false;
            removeBtn.textContent = "♥ Remove";
        }
    });

    actions.appendChild(viewLink);
    actions.appendChild(removeBtn);

    card.appendChild(title);
    card.appendChild(description);
    card.appendChild(actions);

    return card;
}


// Load the current user's favorites
async function loadFavorites(user) {
    favoritesList.textContent = "";
    favoritesEmpty.hidden = true;
    favoritesCount.textContent = "Loading...";

    if (!user) {
        favoritesCount.textContent = "Login required";
        showMessage("Please log in to view your favorites.");
        return;
    }

    try {
        const token = await user.getIdToken();

        const response = await fetch("/favorites", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(
                `Failed to load favorites (${response.status})`
            );
        }

        const data = await response.json();
        const favorites = data.favorites || [];

        // Ignore responses from a previous account
        if (auth.currentUser?.uid !== user.uid) {
            return;
        }

        favoritesList.textContent = "";

        if (favorites.length === 0) {
            favoritesEmpty.hidden = false;
            favoritesCount.textContent = "0 saved articles";
            return;
        }

        favoritesEmpty.hidden = true;

        favorites.forEach(item => {
            favoritesList.appendChild(
                createFavoriteCard(item)
            );
        });

        favoritesCount.textContent =
            `${favorites.length} saved articles`;

    } catch (error) {
        console.error("Favorites loading error:", error);

        if (auth.currentUser?.uid !== user.uid) {
            return;
        }

        favoritesCount.textContent = "Unavailable";

        showMessage(
            "Unable to load favorites. Please try again."
        );
    }
}


// Update header
function updateAuthUI(user) {
    loginBtn.hidden = !!user;
    logoutBtn.hidden = !user;
    userEmail.hidden = !user;

    userEmail.textContent = user?.email || "";
}


// Wait for Firebase login status
onAuthStateChanged(auth, (user) => {
    updateAuthUI(user);
    void loadFavorites(user);
});


// Log out
logoutBtn.addEventListener("click", async () => {
    try {
        await signOut(auth);
    } catch (error) {
        console.error("Logout failed:", error);
        alert("Could not log out.");
    }
});
