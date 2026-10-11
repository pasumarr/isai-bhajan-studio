import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  projectId: "isai-bhajan-studio-app",
  appId: "1:1031408264018:web:59712b657a9bdffc2c908b",
  storageBucket: "isai-bhajan-studio-app.firebasestorage.app",
  apiKey: "AIzaSyAXiiBHomSKtEuc71oNNCmFujgBX0C8URw",
  authDomain: "isai-bhajan-studio-app.firebaseapp.com",
  messagingSenderId: "1031408264018",
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const db = getFirestore(app);

export { app, auth, db };
