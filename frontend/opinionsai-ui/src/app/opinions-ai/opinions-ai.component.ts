import { Component, ElementRef, ViewChild } from '@angular/core';
import { OpinionsAiService, PredictResponse, AnalyzeResponse, TrendPoint } from '../opinions-ai.service';

@Component({
  selector: 'app-opinions-ai',
  templateUrl: './opinions-ai.component.html',
  styleUrls: ['./opinions-ai.component.scss']
})
export class OpinionsAiComponent {
  text: string = '';
  result: PredictResponse | null = null;        // ogólny label/proba (dla istniejącego UI)
  analysis: AnalyzeResponse | null = null;      // nowy wynik: aspekty
  productId: string = 'P001';                   // przykładowy produkt z naszego CSV
  productName: string | null = null;
  trend: TrendPoint[] = [];

  loading = false;
  error: string | null = null;

  @ViewChild('trendCanvas') trendCanvas?: ElementRef<HTMLCanvasElement>;

  constructor(private opinions: OpinionsAiService) {}

  submit() {
    if (!this.text.trim()) return;
    this.loading = true;
    this.error = null;
    this.result = null;
    this.analysis = null;

    this.opinions.analyze(this.text).subscribe({
      next: (res) => {
        this.analysis = res;
        // zachowaj stary format "result", żeby nie zmieniać górnej części UI
        this.result = { label: res.overall_label, proba_positive: res.proba_positive ?? null };
        this.loading = false;
      },
      error: () => { this.error = 'Błąd połączenia z API /analyze'; this.loading = false; }
    });
  }

  reset() {
    this.text = '';
    this.result = null;
    this.analysis = null;
    this.error = null;
  }

  loadTrend() {
    if (!this.productId.trim()) return;
    this.opinions.trend(this.productId.trim()).subscribe({
      next: (res) => {
        this.trend = res.points || [];
        this.productName = res.product_name || null;
        setTimeout(() => this.drawTrend(), 0);
      },
      error: () => { this.error = 'Błąd pobierania trendu'; }
    });
  }

  private drawTrend() {
    const canvas = this.trendCanvas?.nativeElement;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.parentElement ? canvas.parentElement.clientWidth : 640;
    canvas.width = width;
    canvas.height = 220;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!this.trend || this.trend.length === 0) {
      ctx.fillStyle = '#666';
      ctx.fillText('Brak danych dla tego produktu', 20, 30);
      return;
    }

    const pad = { left: 40, right: 20, top: 20, bottom: 40 };
    const W = canvas.width - pad.left - pad.right;
    const H = canvas.height - pad.top - pad.bottom;
    const n = this.trend.length;
    const xStep = W / Math.max(1, n - 1);

    // osie
    ctx.strokeStyle = '#aaa';
    ctx.beginPath();
    ctx.moveTo(pad.left, pad.top);
    ctx.lineTo(pad.left, pad.top + H);
    ctx.lineTo(pad.left + W, pad.top + H);
    ctx.stroke();

    ctx.fillStyle = '#666';
    ctx.fillText('100%', 5, pad.top + 8);
    ctx.fillText('0%', 10, pad.top + H);

    // linia pos_rate (0..1)
    ctx.beginPath();
    this.trend.forEach((pt, i) => {
      const x = pad.left + i * xStep;
      const y = pad.top + (1 - pt.pos_rate) * H;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      ctx.fillRect(x - 2, y - 2, 4, 4);
      if (i % Math.ceil(n / 6) === 0) {
        ctx.fillText(pt.month, x - 15, pad.top + H + 15);
      }
    });
    ctx.strokeStyle = '#2563eb';
    ctx.stroke();
  }
}
