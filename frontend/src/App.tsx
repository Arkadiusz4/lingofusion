// src/App.tsx
import {useState} from "react";
import Header from "./components/Header";
import TranslatePage from "./pages/TranslatePage";
import CorrectPage from "./pages/CorrectPage";
import "./App.css";

function App() {
    // currentPage przechowuje, na której zakładce jesteśmy: "translate" lub "correct"
    const [currentPage, setCurrentPage] = useState<"translate" | "correct">("translate");

    return (
        <div className="app-container">
            {/* Header z tytułem i zakładkami */}
            <Header currentPage={currentPage} onTabChange={setCurrentPage}/>

            {/* Renderujemy stronę w zależności od activeTab */}
            {currentPage === "translate" ? <TranslatePage/> : <CorrectPage/>}
        </div>
    );
}

export default App;
