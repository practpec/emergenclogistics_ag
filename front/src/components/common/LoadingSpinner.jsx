import clsx from 'clsx';

export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizes = { sm: 'h-5 w-5 border-2', md: 'h-8 w-8 border-4' };
  return <div className={clsx('animate-spin rounded-full border-gray-500 border-t-blue-500', sizes[size], className)} />;
};
export default LoadingSpinner;