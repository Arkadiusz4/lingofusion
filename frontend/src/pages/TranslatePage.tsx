// src/pages/TranslatePage.tsx

import {useState} from "react";
import {predict} from "../api";
import TextInput from "../components/TextInput";
import ResultDisplay from "../components/ResultDisplay";
import ModeSelect from "../components/ModeSelect";
import Button from "../components/Button";
import Spinner from "../components/Spinner";
import {AiOutlineSwap} from "react-icons/ai"; // import ikony „swap”
import "./TranslatePage.css";

export default function TranslatePage() {
    const [text, setText] = useState("");
    const [direction, setDirection] = useState<"translate-pl-en" | "translate-en-pl">(
        "translate-pl-en"
    );
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ output: string; highlights?: any[] } | null>(null);

    // Funkcja do zamiany kierunku tłumaczenia
    const swapDirection = () => {
        setDirection((prev) =>
            prev === "translate-pl-en" ? "translate-en-pl" : "translate-pl-en"
        );
    };

    const handleRun = async () => {
        if (!text.trim()) return;
        setLoading(true);
        setResult(null);
        try {
            const payload = {
                text,
                mode: direction,
            } as const;
            const res = await predict(payload);
            setResult(res);
        } catch (err) {
            alert("Coś poszło nie tak 😕");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* ---------- Nagłówek strony: dropdown + swap + przycisk ---------- */}
            <div className="page-header">
                {/* 1) Dropdown kierunku tłumaczenia */}
                <ModeSelect value={direction} onChange={setDirection}/>

                {/* 2) Przycisk swap (podwójna strzałka) */}
                <button
                    type="button"
                    className="swap-button"
                    onClick={swapDirection}
                    aria-label="Zamień kierunek tłumaczenia"
                >
                    <AiOutlineSwap className="swap-icon"/>
                </button>

                {/* 3) Przycisk „Przetłumacz” */}
                <Button onClick={handleRun} disabled={loading || !text.trim()}>
                    {loading ? <Spinner/> : "Przetłumacz"}
                </Button>
            </div>

            {/* ---------- Panele wejścia / wyjścia ---------- */}
            <div className="panels">
                {/* Lewa kolumna: pole wejściowe */}
                <div className="panel panel-input">
                    <label htmlFor="translate-input">
                        {direction === "translate-pl-en" ? "Wejście (PL)" : "Wejście (EN)"}
                    </label>
                    <TextInput
                        id="translate-input"
                        value={text}
                        onChange={setText}
                        placeholder="Wpisz tekst do tłumaczenia..."
                    />
                </div>

                {/* Prawa kolumna: rezultat */}
                <div className="panel panel-output">
                    <label>Wyjście</label>
                    {loading ? (
                        <div className="spinner-wrapper">
                            <Spinner/>
                        </div>
                    ) : (
                        <ResultDisplay
                            output={result?.output || ""}
                            highlights={result?.highlights}
                            dataPlaceholder="Tutaj pojawi się tłumaczenie..."
                        />
                    )}
                </div>
            </div>
        </>
    );
}
