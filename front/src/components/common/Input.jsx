import { forwardRef } from 'react';
import clsx from 'clsx';

export const Input = forwardRef(({ type = 'text', error, className = '', ...props }, ref) => (
  <div>
    <input
      ref={ref}
      type={type}
      className={clsx('w-full px-3 py-2 bg-gray-700 border rounded-md text-gray-100 focus:outline-none focus:ring-2 focus:border-transparent',
        error ? 'border-red-500 ring-red-500' : 'border-gray-600 focus:ring-blue-500',
        'disabled:bg-gray-800 disabled:cursor-not-allowed', className
      )}
      {...props}
    />
    {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
  </div>
));
Input.displayName = 'Input';
export default Input;