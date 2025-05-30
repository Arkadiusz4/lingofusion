import axios from 'axios';

interface PredictRequest {
    text: string;
    mode: 'translate-pl-en' | 'translate-en-pl' | 'gec-en';
}

export async function predict(req: PredictRequest) {
    const {data} = await axios.post('/api/predict', req);
    return data as { output: string; highlights?: { start: number; end: number; suggestion: string }[] };
}
