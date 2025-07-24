import { forwardRef } from 'react';
import clsx from 'clsx';

export const Checkbox = forwardRef(({
  label,
  error,
  className = '',
  ...props
}, ref) => {
  return (
    <div className="flex items-center">
      <label className="flex items-center space-x-2 cursor-pointer">
        <input
          ref={ref}
          type="checkbox"
          className={clsx(
            'h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2',
            className
          )}
          {...props}
        />
        <span className="text-gray-300 select-none">{label}</span>
      </label>
      {error && (
        <p className="mt-1 ml-2 text-sm text-red-400">{error}</p>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

export default Checkbox;