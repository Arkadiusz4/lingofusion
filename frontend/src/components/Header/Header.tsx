import "./Header.css";
import NavTabs from "../NavTabs/NavTabs.tsx";

export default function Header({
                                   currentPage,
                                   onTabChange,
                               }: {
    currentPage: "translate" | "correct";
    onTabChange: (page: "translate" | "correct") => void;
}) {
    return (
        <div className="header">
            <div className="header-logo">
                <img
                    src="/logo-bg.png"
                    alt="LingoFusion Logo"
                    width={50}
                    height={50}
                />
            </div>
            <div className="header-title">LingoFusion</div>
            <NavTabs currentTab={currentPage} onTabChange={onTabChange}/>
        </div>
    );
}
