const API_BASE = "";
const PAGE_SIZE = 10;

let currentStart = 0;
let currentKeyword = "";
let currentArticleId = null;
let hasMoreResults = false;

const elements = {
    keyword: document.getElementById("keyword"),
    author: document.getElementById("author"),
    category: document.getElementById("category"),
    dateFrom: document.getElementById("date-from"),
    dateTo: document.getElementById("date-to"),
    sortBy: document.getElementById("sort-by"),
    results: document.getElementById("results"),
    resultCount: document.getElementById("result-count"),
    resultsTitle: document.getElementById("results-title"),
    loadMore: document.getElementById("load-more"),
    modal: document.getElementById("article-modal"),
    articleDetail: document.getElementById("article-detail")
};

function escapeHtml(value = "") {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    })[character]);
}

function formatDate(value) {
    if (!value) return "Date unavailable";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime())
        ? escapeHtml(value)
        : parsed.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function getSearchParameters() {
    const params = new URLSearchParams();
    if (currentKeyword.trim()) params.set("keyword", currentKeyword.trim());
    if (elements.author.value.trim()) params.set("author", elements.author.value.trim());
    if (elements.category.value) params.set("category", elements.category.value);
    if (elements.dateFrom.value) params.set("date_from", elements.dateFrom.value);
    if (elements.dateTo.value) params.set("date_to", elements.dateTo.value);
    params.set("start", String(currentStart));
    params.set("max_results", String(PAGE_SIZE));
    params.set("sort_by", elements.sortBy.value);
    return params;
}

async function searchArticles(reset = true) {
    if (!currentKeyword.trim() && !elements.author.value.trim() &&
        !elements.category.value && !elements.dateFrom.value && !elements.dateTo.value) {
        elements.results.innerHTML = '<div class="empty-state"><div class="empty-icon">⌕</div><h3>Start with a research question</h3><p>Enter a keyword or select at least one filter to search the arXiv repository.</p></div>';
        elements.resultsTitle.textContent = "Start with a research question";
        elements.resultCount.textContent = "Ready when you are";
        elements.loadMore.hidden = true;
        return;
    }

    if (reset) {
        currentStart = 0;
        elements.results.innerHTML = '<div class="loading-state">Searching scholarly research...</div>';
    }

    elements.resultsTitle.textContent = currentKeyword ? `Results for “${currentKeyword}”` : "Filtered research";
    try {
        const response = await fetch(`${API_BASE}/articles/search?${getSearchParameters()}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Search could not be completed.");

        const articles = data.articles || [];
        const total = data.total_results ?? articles.length;
        elements.resultCount.textContent = `${Number(total).toLocaleString()} papers found`;
        hasMoreResults = currentStart + articles.length < total;
        elements.loadMore.hidden = !hasMoreResults;

        if (reset) elements.results.innerHTML = "";
        if (!articles.length && reset) {
            elements.results.innerHTML = '<div class="empty-state"><div class="empty-icon">⌕</div><h3>No papers found</h3><p>Try another keyword or broaden your filters to discover more research.</p></div>';
            return;
        }
        elements.results.insertAdjacentHTML("beforeend", articles.map(renderArticleCard).join(""));
        currentStart += articles.length;
    } catch (error) {
        elements.results.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
        elements.resultCount.textContent = "Search unavailable";
        elements.loadMore.hidden = true;
    }
}

function renderArticleCard(article) {
    const categories = (article.categories || []).slice(0, 2);
    const authors = (article.authors || []).join(", ") || "Author information unavailable";
    return `
        <article class="article-card">
            <div class="article-meta">
                <span>${escapeHtml(formatDate(article.published))}</span>
                ${categories.map(category => `<span class="category-tag">${escapeHtml(category)}</span>`).join("")}
            </div>
            <button class="article-title" data-article-id="${escapeHtml(article.id)}">${escapeHtml(article.title)}</button>
            <p class="article-authors">${escapeHtml(authors)}</p>
            <p class="article-abstract">${escapeHtml(article.abstract || "No abstract is available for this paper.")}</p>
            <div class="article-actions">
                <button data-article-id="${escapeHtml(article.id)}">Read article details →</button>
                ${article.pdf_url ? `<a href="${escapeHtml(article.pdf_url)}" target="_blank" rel="noopener noreferrer">PDF ↗</a>` : ""}
            </div>
        </article>`;
}


async function recordReadingHistory(articleId) {
    if (typeof window.getFirebaseIdToken !== "function") {
        return;
    }

    let token;

    try {
        token = await window.getFirebaseIdToken();
    } catch {
        // User is not logged in.
        return;
    }

    try {
        const response = await fetch("/history", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                arxiv_id: articleId
            })
        });

        if (!response.ok) {
            console.warn(
                "Could not record reading history:",
                response.status
            );
        }
    } catch (error) {
        console.warn("Reading history unavailable:", error);
    }
}


async function favoriteRequest(articleId, method = "POST") {
    if (typeof window.getFirebaseIdToken !== "function") {
        throw new Error("Please log in first.");
    }

    const token = await window.getFirebaseIdToken();

    const url = method === "DELETE"
        ? `/favorites/${encodeURIComponent(articleId)}`
        : "/favorites";

    const options = {
        method,
        headers: {
            Authorization: `Bearer ${token}`
        }
    };

    if (method === "POST") {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify({
            arxiv_id: articleId
        });
    }

    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || "Favorite request failed"
        );
    }

    return data;
}

async function checkFavorite(articleId) {
    const token = await window.getFirebaseIdToken();

    const response = await fetch(
        `/favorites/${encodeURIComponent(articleId)}`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    if (!response.ok) {
        throw new Error("Failed to check favorite status");
    }

    return response.json();
}


async function setupFavoriteButton(articleId) {
    const button = document.getElementById("favorite-btn");
    if (!button) return;

    button.dataset.articleId = articleId;
    button.disabled = true;
    button.textContent = "Loading...";

    let isFavorited = false;

    function updateButton() {
        button.textContent = isFavorited
            ? "♥ Saved"
            : "♡ Save to Favorites";
    }

    try {
        const status = await checkFavorite(articleId);

        if (button.dataset.articleId !== articleId) return;

        isFavorited = status.is_favorited;
        updateButton();
    } catch (error) {
        if (button.dataset.articleId !== articleId) return;

        button.textContent = "Log in to save";
        button.disabled = false;
    }

    button.disabled = false;

    button.onclick = async () => {
        button.disabled = true;

        try {
            if (isFavorited) {
                await favoriteRequest(articleId, "DELETE");
                isFavorited = false;
            } else {
                await favoriteRequest(articleId, "POST");
                isFavorited = true;
            }

            updateButton();

        } catch (error) {
            alert(error.message);

        } finally {
            button.disabled = false;
        }
    };
}


async function openArticle(articleId) {
    currentArticleId = articleId;
    elements.modal.classList.add("open");
    elements.modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    elements.articleDetail.innerHTML = '<div class="loading-state">Loading article details...</div>';

    try {
        const response = await fetch(`${API_BASE}/articles/${encodeURIComponent(articleId)}`);
        const article = await response.json();
        if (!response.ok) throw new Error(article.detail || "Article could not be loaded.");

        // Record history after article details load successfully
        void recordReadingHistory(articleId);
        void setupFavoriteButton(articleId);

        elements.articleDetail.innerHTML = `
            <div class="detail-category">${escapeHtml((article.categories || []).join(" · "))}</div>
            <h2 id="article-title">${escapeHtml(article.title)}</h2>
            <p class="detail-authors">${escapeHtml((article.authors || []).join(", "))}<br>Published ${escapeHtml(formatDate(article.published))} · arXiv:${escapeHtml(article.id)}</p>
            <p class="detail-abstract">${escapeHtml(article.abstract || "No abstract available.")}</p>
            <div class="detail-links">
                <a href="${escapeHtml(article.article_url)}" target="_blank" rel="noopener noreferrer">View on arXiv ↗</a>
                ${article.pdf_url ? `<a href="${escapeHtml(article.pdf_url)}" target="_blank" rel="noopener noreferrer">Read PDF ↗</a>` : ""}
            </div>
            <section class="discussion-box">
                <h3>Community discussion</h3>
                <p class="discussion-intro">Share an insight or ask a question about this paper.</p>
                <form class="discussion-form" id="discussion-form">
                    <input id="discussion-author" name="author_name" maxlength="80" placeholder="Your name" required>
                    <textarea id="discussion-content" name="content" maxlength="3000" placeholder="What did you think about this research?" required></textarea>
                    <button class="button button-primary" type="submit">Post to discussion →</button>
                </form>
                <div id="discussion-list"><div class="loading-state">Loading discussion...</div></div>
            </section>`;
        await loadDiscussions(articleId);
    } catch (error) {
        elements.articleDetail.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
    }
}

async function loadDiscussions(articleId) {
    const list = document.getElementById("discussion-list");
    if (!list) return;
    try {
        const response = await fetch(`${API_BASE}/articles/${encodeURIComponent(articleId)}/discussions`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Could not load discussion.");
        const posts = data.discussions || [];
        list.innerHTML = posts.length ? posts.map(post => `
            <article class="discussion-post">
                <strong>${escapeHtml(post.author_name)}</strong>
                <time>${escapeHtml(formatDate(post.created_at))}</time>
                <p>${escapeHtml(post.content)}</p>
            </article>`).join("") : '<p class="discussion-intro">No comments yet. Start the conversation.</p>';
    } catch (error) {
        list.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
    }
}

async function submitDiscussion(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const authorName = document.getElementById("discussion-author").value.trim();
    const content = document.getElementById("discussion-content").value.trim();
    if (!authorName || !content || !currentArticleId) return;

    const submitButton = form.querySelector("button[type='submit']");
    submitButton.disabled = true;
    submitButton.textContent = "Posting...";
    try {
        const response = await fetch(`${API_BASE}/articles/${encodeURIComponent(currentArticleId)}/discussions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                arxiv_id: currentArticleId,
                author_name: authorName,
                content
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Your post could not be saved.");
        form.reset();
        await loadDiscussions(currentArticleId);
    } catch (error) {
        alert(error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Post to discussion →";
    }
}

function closeArticle() {
    elements.modal.classList.remove("open");
    elements.modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    currentArticleId = null;
}

document.getElementById("search-button").addEventListener("click", () => {
    currentKeyword = elements.keyword.value;
    searchArticles(true);
});
elements.keyword.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        currentKeyword = elements.keyword.value;
        searchArticles(true);
    }
});
document.getElementById("apply-filters").addEventListener("click", () => searchArticles(true));
document.getElementById("clear-filters").addEventListener("click", () => {
    elements.author.value = "";
    elements.category.value = "";
    elements.dateFrom.value = "";
    elements.dateTo.value = "";
    elements.sortBy.value = "relevance";
    currentKeyword = elements.keyword.value;
    searchArticles(true);
});
document.getElementById("load-more").addEventListener("click", () => searchArticles(false));
document.querySelectorAll("[data-query]").forEach(button => {
    button.addEventListener("click", () => {
        elements.keyword.value = button.dataset.query;
        currentKeyword = button.dataset.query;
        searchArticles(true);
    });
});
elements.results.addEventListener("click", event => {
    const target = event.target.closest("[data-article-id]");
    if (target) openArticle(target.dataset.articleId);
});
elements.modal.addEventListener("click", event => {
    if (event.target.matches("[data-close-modal]")) closeArticle();
});
document.addEventListener("keydown", event => {
    if (event.key === "Escape" && elements.modal.classList.contains("open")) closeArticle();
});
elements.articleDetail.addEventListener("submit", event => {
    if (event.target.id === "discussion-form") submitDiscussion(event);
});
