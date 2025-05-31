import {useState} from "react";
import Header from "./components/Header/Header.tsx";
import TranslatePage from "./pages/TranslatePage/TranslatePage";
import CorrectPage from "./pages/CorrectPage/CorrectPage";
import "./App.css";

function App() {
    const [currentPage, setCurrentPage] = useState<"translate" | "correct">("translate");

    return (
        <div className="app-container">
            <Header currentPage={currentPage} onTabChange={setCurrentPage}/>

            {currentPage === "translate" ? <TranslatePage/> : <CorrectPage/>}
        </div>
    );
}

export default App;
