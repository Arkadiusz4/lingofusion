import {useState} from "react";
import {predict} from "../../api";
import TextInput from "../../components/TextInput/TextInput";
import ResultDisplay from "../../components/ResultDisplay/ResultDisplay";
import Button from "../../components/Button/Button.tsx";
import Spinner from "../../components/Spinner/Spinner";
import "./CorrectPage.css";

export default function CorrectPage() {
    const [text, setText] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ output: string; highlights?: any[] } | null>(null);

    const handleRun = async () => {
        if (!text.trim()) return;
        setLoading(true);
        setResult(null);
        try {
            const payload = {
                text,
                mode: "gec-en" as const,
            };
            const res = await predict(payload);
            setResult(res);
        } catch {
            alert("Coś poszło nie tak 😕");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <div className="correct-header">
                <Button onClick={handleRun} disabled={loading || !text.trim()}>
                    {loading ? <Spinner/> : "Sprawdź"}
                </Button>
            </div>

            <div className="panels">
                <div className="panel panel-input">
                    <label htmlFor="correct-input">Wejście (EN)</label>
                    <TextInput
                        id="correct-input"
                        value={text}
                        onChange={setText}
                        placeholder="Wpisz tekst do korekty..."
                    />
                </div>

                <div className="panel panel-output">
                    <label>Poprawka</label>
                    {loading ? (
                        <div className="spinner-wrapper">
                            <Spinner/>
                        </div>
                    ) : (
                        <ResultDisplay
                            output={result?.output || ""}
                            highlights={result?.highlights}
                            dataPlaceholder="Tutaj pojawi się korekta..."
                        />
                    )}
                </div>
            </div>
        </>
    );
}
