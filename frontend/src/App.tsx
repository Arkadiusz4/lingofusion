import {useState} from 'react';
import {predict} from './api';
import TextInput from './components/TextInput';
import ResultDisplay from './components/ResultDisplay';
import ModeToggle from './components/ModeToggle';
import Button from './components/Button';
import Spinner from './components/Spinner';
import './App.css';

function App() {
    const [text, setText] = useState('');
    const [mode, setMode] = useState<'translate' | 'gec'>('translate');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ output: string; highlights?: any[] } | null>(null);

    const handleRun = async () => {
        if (!text.trim()) return;
        setLoading(true);
        try {
            const payload = {
                text,
                mode: mode === 'translate' ? 'translate-pl-en' : 'gec-en'
            } as const;
            const res = await predict(payload);
            setResult(res);
        } catch {
            alert('Coś poszło nie tak 😕');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-container">
            <header>
                <h1>Translator & Korektor</h1>
            </header>

            <div className="panels">
                <div className="panel panel--input">
                    <label>
                        {mode === 'translate' ? 'Wejście (PL)' : 'Wejście (EN)'}
                    </label>
                    <TextInput
                        value={text}
                        onChange={setText}
                        placeholder="Wpisz tekst..."
                    />
                    {/* Teraz toggle pod polem */}
                    <div className="toggle-wrapper">
                        <ModeToggle mode={mode} onChange={setMode}/>
                    </div>
                </div>

                <div className="panel panel--output">
                    <label>
                        {mode === 'translate' ? 'Wyjście (EN)' : 'Poprawka'}
                    </label>
                    {loading ? (
                        <Spinner/>
                    ) : (
                        <ResultDisplay
                            output={result?.output || ''}
                            highlights={result?.highlights}
                            dataPlaceholder="Wynik pojawi się tutaj..."
                        />
                    )}
                </div>
            </div>

            <footer>
                <Button onClick={handleRun} disabled={loading || !text.trim()}>
                    {loading ? <Spinner/> : mode === 'translate' ? 'Tłumacz' : 'Korektuj'}
                </Button>
            </footer>
        </div>
    );
}

export default App;
