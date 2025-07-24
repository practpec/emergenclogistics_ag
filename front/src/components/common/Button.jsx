import { forwardRef } from 'react';
import clsx from 'clsx';

export const Button = forwardRef(({ children, variant = 'primary', size = 'md', disabled = false, className = '', ...props }, ref) => {
  const base = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white focus:ring-gray-500',
  };
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2 text-base' };
  return <button ref={ref} disabled={disabled} className={clsx(base, variants[variant], sizes[size], className)} {...props}>{children}</button>;
});
Button.displayName = 'Button';
export default Button;