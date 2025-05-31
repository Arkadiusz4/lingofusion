import NavTabs from "./NavTabs";
import "./Header.css";

interface Props {
    currentPage: "translate" | "correct";
    onTabChange: (page: "translate" | "correct") => void;
}

export default function Header({currentPage, onTabChange}: Props) {
    return (
        <header className="header">
            <div className="header-title">LingoFusion</div>
            <NavTabs currentTab={currentPage} onTabChange={onTabChange}/>
        </header>
    );
}
