import axios from 'axios';

export interface PredictRequest {
  text: string;
  mode: 'translate-pl-en' | 'gec-en';
}

export interface PredictResponse {
    output: string;
    highlights?: { start: number; end: number; suggestion: string }[];
}

export async function predict(req: PredictRequest): Promise<PredictResponse> {
    const {data} = await axios.post<PredictResponse>(
        'http://localhost:8000/api/predict',
        req
    );
    return data;
}
