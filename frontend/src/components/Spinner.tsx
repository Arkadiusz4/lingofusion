import "./Spinner.css";

export default function Spinner() {
    return (
        <div className="spinner" aria-label="Ładowanie">
            <div className="double-bounce1"></div>
            <div className="double-bounce2"></div>
        </div>
    );
}
