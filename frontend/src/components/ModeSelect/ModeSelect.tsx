import "./ModeSelect.css";

interface Props {
    value: "translate-pl-en" | "translate-en-pl";
    onChange: (v: "translate-pl-en" | "translate-en-pl") => void;
}

export default function ModeSelect({value, onChange}: Props) {
    return (
        <select
            className="mode-select"
            value={value}
            onChange={(e) => onChange(e.target.value as "translate-pl-en" | "translate-en-pl")}
            aria-label="Wybierz kierunek tłumaczenia"
        >
            <option value="translate-pl-en">Polski → Angielski</option>
            <option value="translate-en-pl">Angielski → Polski</option>
        </select>
    );
}
