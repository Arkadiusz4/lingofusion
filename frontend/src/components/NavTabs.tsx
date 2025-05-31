import {FiGlobe, FiEdit} from "react-icons/fi";
import "./NavTabs.css";

interface Props {
    currentTab: "translate" | "correct";
    onTabChange: (tab: "translate" | "correct") => void;
}

export default function NavTabs({currentTab, onTabChange}: Props) {
    return (
        <div className="nav-tabs">
            <button
                className={`tab-button ${currentTab === "translate" ? "active" : ""}`}
                onClick={() => onTabChange("translate")}
            >
                <FiGlobe className="tab-icon"/>
                <span className="tab-text">Tłumaczenie</span>
            </button>
            <button
                className={`tab-button ${currentTab === "correct" ? "active" : ""}`}
                onClick={() => onTabChange("correct")}
            >
                <FiEdit className="tab-icon"/>
                <span className="tab-text">Korekta EN</span>
            </button>
        </div>
    );
}
