import { useEffect, useRef } from 'react';
import {
  Chart,
  BarController,
  LineController,
  DoughnutController,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

Chart.register(
  BarController,
  LineController,
  DoughnutController,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Filler
);

// Cores do tema escuro do NextBarber (src/styles/global.css)
Chart.defaults.color = '#a1a1aa';
Chart.defaults.borderColor = '#232327';
Chart.defaults.font.family = "'Inter', -apple-system, 'Segoe UI', Roboto, Arial, sans-serif";

/**
 * Envolve o Chart.js: cria o grafico no canvas e o destroi ao desmontar.
 * A API do dashboard ja devolve labels e valores alinhados para o Chart.js.
 */
export default function Grafico({ tipo, dados, opcoes, altura = 260, descricao }) {
  const canvas = useRef(null);

  useEffect(() => {
    const grafico = new Chart(canvas.current, {
      type: tipo,
      data: dados,
      options: { responsive: true, maintainAspectRatio: false, ...opcoes }
    });
    return () => grafico.destroy();
  }, [tipo, dados, opcoes]);

  return (
    <div className="grafico" style={{ height: altura }}>
      <canvas ref={canvas} role="img" aria-label={descricao} />
    </div>
  );
}
