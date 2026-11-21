
import { initializeApp } from
  "https://www.gstatic.com/firebasejs/13.4.0/firebase-app.js";

import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCwuBB2YBrbfEznhDKk4dhgL21xqbqW-Hs",
  authDomain: "scholarly-insights-2aac8.firebaseapp.com",
  projectId: "scholarly-insights-2aac8",
  storageBucket: "scholarly-insights-2aac8.firebasestorage.app",
  messagingSenderId: "197894445442",
  appId: "1:197894445442:web:bacfd7e60e850e9d0e579b"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// Login-page elements
const authForm = document.getElementById("auth-form");
const authSwitch = document.getElementById("auth-switch");
const authSubmit = document.getElementById("auth-submit");
const authError = document.getElementById("auth-error");
const authTitle = document.getElementById("auth-title");
const authDescription = document.getElementById("auth-description");
const authPassword = document.getElementById("auth-password");

// Homepage elements
const loginBtn = document.getElementById("login-btn");
const logoutBtn = document.getElementById("logout-btn");
const userEmail = document.getElementById("user-email");

let isSignUp = false;


async function syncUser(user) {
  const token = await user.getIdToken();

  const response = await fetch("/auth/sync", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));

    throw new Error(
      data.detail || "Failed to sync account with backend"
    );
  }

  return response.json();
}


// Update login/sign-up form
function updateAuthMode() {
  if (!authForm) return;

  if (authTitle) {
    authTitle.textContent = isSignUp
      ? "Create your account"
      : "Welcome back";
  }

  if (authDescription) {
    authDescription.textContent = isSignUp
      ? "Join Scholarly Insights and organize your research."
      : "Log in to continue your research journey.";
  }

  if (authSubmit) {
    authSubmit.textContent = isSignUp
      ? "Create account →"
      : "Log in →";
  }

  if (authSwitch) {
    authSwitch.textContent = isSignUp
      ? "Already have an account? Log in"
      : "Create an account";
  }

  if (authPassword) {
    authPassword.autocomplete = isSignUp
      ? "new-password"
      : "current-password";
  }

  if (authError) authError.textContent = "";
}

// Switch between Login and Sign Up
if (authSwitch) {
  authSwitch.addEventListener("click", () => {
    isSignUp = !isSignUp;
    updateAuthMode();
  });
}

// Handle Login / Sign Up
if (authForm) {
  authForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document
      .getElementById("auth-email")
      .value.trim();

    const password = authPassword.value;

    authSubmit.disabled = true;
    if (authError) authError.textContent = "";


    try {
      let result;

      if (isSignUp) {
        result = await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );
      } else {
        result = await signInWithEmailAndPassword(
          auth,
          email,
          password
        );
      }

      // Synchronize Firebase user with SQLite
      await syncUser(result.user);

      // Redirect only after successful synchronization
      window.location.href = "/";

    } catch (error) {
      console.error("Authentication failed:", error);

      if (authError) {
        authError.textContent =
          error.message || "Authentication failed.";
      }
    } finally {
      authSubmit.disabled = false;
    }
  });
}

// Handle Logout on homepage
if (logoutBtn) {
  logoutBtn.addEventListener("click", async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  });
}

// Listen for authentication state changes
onAuthStateChanged(auth, (user) => {
  if (loginBtn) loginBtn.hidden = !!user;
  if (logoutBtn) logoutBtn.hidden = !user;

  if (userEmail) {
    userEmail.hidden = !user;
    userEmail.textContent = user?.email || "";
  }
});

// Helper function for protected backend requests
window.getFirebaseIdToken = async () => {
  const user = auth.currentUser;

  if (!user) {
    throw new Error("Please log in first.");
  }

  return user.getIdToken();
};