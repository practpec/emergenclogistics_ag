import clsx from 'clsx';

export const Card = ({ children, className = '', ...props }) => {
  return (
    <div
      className={clsx(
        // Clases base para el componente Card
        'bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-md',
        // Permite añadir clases personalizadas desde fuera
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

