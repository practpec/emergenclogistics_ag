import { useRef, useEffect } from 'react';

// Componente de gráfica de líneas usando Canvas
export const LineChart = ({ data, width = 400, height = 200, className = '' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.datasets) return;

    const ctx = canvas.getContext('2d');
    const { width: canvasWidth, height: canvasHeight } = canvas;
    
    // Limpiar canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    // Configuración
    const padding = 40;
    const chartWidth = canvasWidth - 2 * padding;
    const chartHeight = canvasHeight - 2 * padding;
    
    // Encontrar valores min/max
    const allValues = data.datasets.flatMap(dataset => dataset.data);
    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);
    const valueRange = maxValue - minValue || 1;
    
    // Dibujar fondo
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    
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
    const stepX = chartWidth / (data.labels.length - 1);
    for (let i = 0; i < data.labels.length; i++) {
      const x = padding + i * stepX;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, canvasHeight - padding);
      ctx.stroke();
    }
    
    // Dibujar datasets
    data.datasets.forEach((dataset, datasetIndex) => {
      ctx.strokeStyle = dataset.borderColor || '#3b82f6';
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      dataset.data.forEach((value, index) => {
        const x = padding + index * stepX;
        const y = canvasHeight - padding - ((value - minValue) / valueRange) * chartHeight;
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.stroke();
      
      // Dibujar puntos
      ctx.fillStyle = dataset.borderColor || '#3b82f6';
      dataset.data.forEach((value, index) => {
        const x = padding + index * stepX;
        const y = canvasHeight - padding - ((value - minValue) / valueRange) * chartHeight;
        
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fill();
      });
    });
    
    // Dibujar etiquetas del eje Y
    ctx.fillStyle = '#9ca3af';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    
    for (let i = 0; i <= 5; i++) {
      const value = minValue + (valueRange * (5 - i) / 5);
      const y = padding + (i * chartHeight / 5);
      ctx.fillText(value.toFixed(1), padding - 10, y + 3);
    }
    
    // Dibujar etiquetas del eje X
    ctx.textAlign = 'center';
    data.labels.forEach((label, index) => {
      if (index % Math.ceil(data.labels.length / 8) === 0) {
        const x = padding + index * stepX;
        ctx.fillText(label, x, canvasHeight - 10);
      }
    });
    
  }, [data, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className={`border border-gray-600 rounded ${className}`}
    />
  );
};

// Componente de gráfica de barras
export const BarChart = ({ data, width = 400, height = 200, className = '' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.datasets) return;

    const ctx = canvas.getContext('2d');
    const { width: canvasWidth, height: canvasHeight } = canvas;
    
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    const padding = 40;
    const chartWidth = canvasWidth - 2 * padding;
    const chartHeight = canvasHeight - 2 * padding;
    
    const maxValue = Math.max(...data.datasets[0].data);
    const barWidth = chartWidth / data.labels.length * 0.6;
    const barSpacing = chartWidth / data.labels.length;
    
    // Fondo
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    
    // Barras
    data.datasets[0].data.forEach((value, index) => {
      const barHeight = (value / maxValue) * chartHeight;
      const x = padding + index * barSpacing + (barSpacing - barWidth) / 2;
      const y = canvasHeight - padding - barHeight;
      
      const color = data.datasets[0].backgroundColor[index] || '#3b82f6';
      ctx.fillStyle = color;
      ctx.fillRect(x, y, barWidth, barHeight);
      
      // Valor encima de la barra
      ctx.fillStyle = '#e5e7eb';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(value.toFixed(1), x + barWidth / 2, y - 5);
    });
    
    // Etiquetas
    ctx.fillStyle = '#9ca3af';
    ctx.font = '10px Arial';
    data.labels.forEach((label, index) => {
      const x = padding + index * barSpacing + barSpacing / 2;
      ctx.save();
      ctx.translate(x, canvasHeight - 10);
      ctx.rotate(-Math.PI / 4);
      ctx.textAlign = 'right';
      ctx.fillText(label, 0, 0);
      ctx.restore();
    });
    
  }, [data, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className={`border border-gray-600 rounded ${className}`}
    />
  );
};

// Componente de gráfica de dona/pie
export const PieChart = ({ data, width = 300, height = 300, className = '' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.datasets) return;

    const ctx = canvas.getContext('2d');
    const { width: canvasWidth, height: canvasHeight } = canvas;
    
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    const centerX = canvasWidth / 2;
    const centerY = canvasHeight / 2;
    const radius = Math.min(centerX, centerY) - 20;
    
    // Fondo
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    
    const total = data.datasets[0].data.reduce((sum, value) => sum + value, 0);
    let currentAngle = -Math.PI / 2;
    
    // Dibujar segmentos
    data.datasets[0].data.forEach((value, index) => {
      const sliceAngle = (value / total) * 2 * Math.PI;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      
      const color = data.datasets[0].backgroundColor[index] || `hsl(${index * 60}, 70%, 50%)`;
      ctx.fillStyle = color;
      ctx.fill();
      
      ctx.strokeStyle = '#1f2937';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Etiqueta
      if (value > 0) {
        const labelAngle = currentAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
        const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
        
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${((value / total) * 100).toFixed(1)}%`, labelX, labelY);
      }
      
      currentAngle += sliceAngle;
    });
    
  }, [data, width, height]);

  return (
    <div className="flex items-center space-x-4">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className={`border border-gray-600 rounded ${className}`}
      />
      
      {/* Leyenda */}
      <div className="space-y-2">
        {data.labels.map((label, index) => (
          <div key={index} className="flex items-center space-x-2 text-sm">
            <div
              className="w-4 h-4 rounded"
              style={{
                backgroundColor: data.datasets[0].backgroundColor[index] || `hsl(${index * 60}, 70%, 50%)`
              }}
            />
            <span className="text-gray-300">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Componente de métricas
export const MetricCard = ({ title, value, subtitle, variant = 'default' }) => {
  const variants = {
    default: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    danger: 'text-red-400',
    info: 'text-purple-400'
  };

  return (
    <div className="bg-gray-800 border border-gray-600 rounded-lg p-4 text-center">
      <h3 className="text-sm font-medium text-gray-300 mb-1">{title}</h3>
      <p className={`text-2xl font-bold ${variants[variant]} mb-1`}>{value}</p>
      {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
    </div>
  );
};

// Componente de tabla responsiva
export const DataTable = ({ headers, rows, className = '' }) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-600">
            {headers.map((header, index) => (
              <th key={index} className="text-left py-2 px-3 font-medium text-gray-300">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="border-b border-gray-700 hover:bg-gray-700">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="py-2 px-3 text-gray-200">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};