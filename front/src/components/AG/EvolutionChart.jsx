import { useRef, useEffect } from 'react';
import { Card } from '../UI';

const EvolutionChart = ({ evolutionData, className = '' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !evolutionData || evolutionData.length === 0) return;

    const ctx = canvas.getContext('2d');
    const { width: canvasWidth, height: canvasHeight } = canvas;
    
    // Limpiar canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    // Configuración
    const padding = 60;
    const chartWidth = canvasWidth - 2 * padding;
    const chartHeight = canvasHeight - 2 * padding;
    
    // Encontrar valores min/max
    const allBest = evolutionData.map(d => parseFloat(d.mejor) || 0);
    const allAvg = evolutionData.map(d => parseFloat(d.promedio) || 0);
    const allWorst = evolutionData.map(d => parseFloat(d.peor) || 0);
    
    const minValue = Math.min(...allBest, ...allAvg, ...allWorst);
    const maxValue = Math.max(...allBest, ...allAvg, ...allWorst);
    const valueRange = maxValue - minValue || 1;
    
    // Dibujar fondo
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    
    // Título
    ctx.fillStyle = '#fbbf24';
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Evolución del Fitness por Generación', canvasWidth / 2, 30);
    
    // Dibujar grid
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;
    
    // Grid horizontal
    for (let i = 0; i <= 5; i++) {
      const y = padding + (i * chartHeight / 5);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvasWidth - padding, y);
      ctx.stroke();
    }
    
    // Grid vertical
    const stepX = chartWidth / (evolutionData.length - 1);
    for (let i = 0; i < evolutionData.length; i += Math.ceil(evolutionData.length / 10)) {
      const x = padding + i * stepX;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, padding + chartHeight);
      ctx.stroke();
    }
    
    // Función auxiliar para calcular Y
    const getY = (value) => padding + chartHeight - ((value - minValue) / valueRange) * chartHeight;
    
    // Dibujar línea del mejor fitness
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    evolutionData.forEach((data, index) => {
      const x = padding + index * stepX;
      const y = getY(parseFloat(data.mejor) || 0);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
    
    // Dibujar línea del promedio
    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    evolutionData.forEach((data, index) => {
      const x = padding + index * stepX;
      const y = getY(parseFloat(data.promedio) || 0);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
    
    // Dibujar línea del peor fitness
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    evolutionData.forEach((data, index) => {
      const x = padding + index * stepX;
      const y = getY(parseFloat(data.peor) || 0);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
    
    // Dibujar puntos destacados cada 10 generaciones
    evolutionData.forEach((data, index) => {
      if (index % 10 === 0 || index === evolutionData.length - 1) {
        const x = padding + index * stepX;
        
        // Punto mejor
        ctx.fillStyle = '#3b82f6';
        ctx.beginPath();
        ctx.arc(x, getY(parseFloat(data.mejor) || 0), 4, 0, 2 * Math.PI);
        ctx.fill();
        
        // Punto promedio
        ctx.fillStyle = '#22c55e';
        ctx.beginPath();
        ctx.arc(x, getY(parseFloat(data.promedio) || 0), 3, 0, 2 * Math.PI);
        ctx.fill();
        
        // Punto peor
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(x, getY(parseFloat(data.peor) || 0), 3, 0, 2 * Math.PI);
        ctx.fill();
      }
    });
    
    // Etiquetas del eje Y
    ctx.fillStyle = '#9ca3af';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    
    for (let i = 0; i <= 5; i++) {
      const value = minValue + (valueRange * (5 - i) / 5);
      const y = padding + (i * chartHeight / 5);
      ctx.fillText(value.toFixed(1), padding - 10, y + 3);
    }
    
    // Etiquetas del eje X
    ctx.textAlign = 'center';
    const labelStep = Math.ceil(evolutionData.length / 8);
    evolutionData.forEach((data, index) => {
      if (index % labelStep === 0 || index === evolutionData.length - 1) {
        const x = padding + index * stepX;
        ctx.fillText(data.generacion?.toString() || index.toString(), x, canvasHeight - 20);
      }
    });
    
    // Título de ejes
    ctx.fillStyle = '#9ca3af';
    ctx.font = '14px Arial';
    
    // Eje X
    ctx.textAlign = 'center';
    ctx.fillText('Generaciones', canvasWidth / 2, canvasHeight - 5);
    
    // Eje Y
    ctx.save();
    ctx.translate(15, canvasHeight / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Valor de Fitness', 0, 0);
    ctx.restore();
    
    // Leyenda
    const legendY = padding + 20;
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    
    // Mejor fitness
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(canvasWidth - 150, legendY);
    ctx.lineTo(canvasWidth - 130, legendY);
    ctx.stroke();
    ctx.fillStyle = '#e5e7eb';
    ctx.fillText('Mejor Fitness', canvasWidth - 125, legendY + 3);
    
    // Promedio
    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(canvasWidth - 150, legendY + 20);
    ctx.lineTo(canvasWidth - 130, legendY + 20);
    ctx.stroke();
    ctx.fillStyle = '#e5e7eb';
    ctx.fillText('Promedio', canvasWidth - 125, legendY + 23);
    
    // Peor fitness
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(canvasWidth - 150, legendY + 40);
    ctx.lineTo(canvasWidth - 130, legendY + 40);
    ctx.stroke();
    ctx.fillStyle = '#e5e7eb';
    ctx.fillText('Peor Fitness', canvasWidth - 125, legendY + 43);
    
  }, [evolutionData]);

  if (!evolutionData || evolutionData.length === 0) {
    return (
      <Card className={className}>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Evolución del Fitness</h3>
        <div className="text-center text-gray-400 py-8">
          <p>No hay datos de evolución disponibles</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <h3 className="text-xl font-semibold text-yellow-400 mb-4">Evolución del Fitness</h3>
      <div className="flex justify-center">
        <canvas
          ref={canvasRef}
          width={800}
          height={400}
          className="border border-gray-600 rounded max-w-full h-auto"
        />
      </div>
      <div className="mt-4 text-sm text-gray-400">
        <p className="text-center">
          Gráfica que muestra la evolución del fitness a través de {evolutionData.length} generaciones.
          La línea azul representa el mejor individuo, la verde el promedio poblacional y la roja el peor.
        </p>
      </div>
    </Card>
  );
};

export default EvolutionChart;