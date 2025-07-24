import { useEffect, useRef } from 'react';
import { Card } from '../../common/Card';

const EvolutionChart = ({ evolutionData }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !evolutionData || evolutionData.length === 0) return;

    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    const padding = 50;
    
    const best = evolutionData.map(d => d.mejor);
    const avg = evolutionData.map(d => d.promedio);
    const worst = evolutionData.map(d => d.peor);
    const maxVal = Math.max(...best);
    const minVal = Math.min(...worst);
    const range = maxVal - minVal || 1;
    const stepX = (width - 2 * padding) / (evolutionData.length - 1);

    const scaleY = val => height - padding - ((val - minVal) / range) * (height - 2 * padding);
    
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#1f2937'; // bg-gray-800
    ctx.fillRect(0, 0, width, height);

    const drawLine = (data, color, lineWidth) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      ctx.moveTo(padding, scaleY(data[0]));
      data.forEach((point, i) => {
        ctx.lineTo(padding + i * stepX, scaleY(point));
      });
      ctx.stroke();
    };

    drawLine(worst, '#ef4444', 1.5); // red-500
    drawLine(avg, '#3b82f6', 2); // blue-500
    drawLine(best, '#22c55e', 3); // green-500

    ctx.fillStyle = '#9ca3af';
    ctx.font = '10px Arial';
    for (let i = 0; i <= 5; i++) {
        const val = minVal + (range / 5) * i;
        ctx.fillText(val.toFixed(0), 5, height - padding - (i/5) * (height-2*padding));
    }
    ctx.fillText('Gen 1', padding, height - 20);
    ctx.fillText(`Gen ${evolutionData[evolutionData.length - 1].generacion}`, width-padding-20, height-20);

  }, [evolutionData]);

  return (
    <Card>
      <h2 className="text-xl font-semibold text-blue-400 mb-3">Evolución del Fitness</h2>
      <canvas ref={canvasRef} width="600" height="300" className="w-full h-auto"></canvas>
    </Card>
  );
};

export default EvolutionChart;