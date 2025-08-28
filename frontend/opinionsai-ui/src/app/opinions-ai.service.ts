import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PredictResponse {
  label: number;
  proba_positive?: number | null;
}

export interface Aspect {
  name: string;
  score: number;   // 0..1
  label: number;   // 0/1
  examples: string[];
  count: number;
}

export interface AnalyzeResponse {
  overall_label: number;
  proba_positive?: number | null;
  aspects: Aspect[];
}

export interface TrendPoint {
  month: string;      // "2025-03"
  pos_rate: number;   // 0..1
  avg_rating: number; // 1..5
  count: number;
}

@Injectable({ providedIn: 'root' })
export class OpinionsAiService {
  private readonly API_BASE = 'http://localhost:8000'; // to samo co w swaggerze

  constructor(private http: HttpClient) { }

  analyze(text: string) { return this.http.post<AnalyzeResponse>(`${this.API_BASE}/analyze`, { text }); }
  predict(text: string) { return this.http.post<PredictResponse>(`${this.API_BASE}/predict/baseline`, { text }); }

  trend(productId: string): Observable<{ product_id: string; product_name: string | null; points: TrendPoint[] }> {
    return this.http.get<{ product_id: string; product_name: string | null; points: TrendPoint[] }>(
      `${this.API_BASE}/trend/${productId}`
    );
  }
}
