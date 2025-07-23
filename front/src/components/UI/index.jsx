import { forwardRef } from 'react'
import clsx from 'clsx'

// Button Component
export const Button = forwardRef(({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false,
  className = '',
  ...props 
}, ref) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500'
  }
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }
  
  return (
    <button
      ref={ref}
      disabled={disabled}
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
})

Button.displayName = 'Button'

// Input Component
export const Input = forwardRef(({ 
  type = 'text',
  error,
  className = '',
  ...props 
}, ref) => {
  return (
    <div>
      <input
        ref={ref}
        type={type}
        className={clsx(
          'w-full px-3 py-2 bg-gray-700 border rounded-md text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          error ? 'border-red-500' : 'border-gray-600',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}
    </div>
  )
})

Input.displayName = 'Input'

// Select Component
export const Select = forwardRef(({ 
  options = [],
  error,
  className = '',
  ...props 
}, ref) => {
  return (
    <div>
      <select
        ref={ref}
        className={clsx(
          'w-full px-3 py-2 bg-gray-700 border rounded-md text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          error ? 'border-red-500' : 'border-gray-600',
          className
        )}
        {...props}
      >
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}
    </div>
  )
})

Select.displayName = 'Select'

// Checkbox Component
export const Checkbox = forwardRef(({ 
  label,
  error,
  className = '',
  ...props 
}, ref) => {
  return (
    <div>
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
        <span className="text-gray-300">{label}</span>
      </label>
      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}
    </div>
  )
})

Checkbox.displayName = 'Checkbox'

// Loading Spinner Component
export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  }
  
  return (
    <div className={clsx('animate-spin rounded-full border-2 border-gray-600 border-t-blue-500', sizes[size], className)} />
  )
}

// Card Component
export const Card = ({ children, className = '', ...props }) => {
  return (
    <div
      className={clsx(
        'bg-gray-800 border border-gray-600 rounded-lg p-6',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// Badge Component
export const Badge = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-gray-600 text-gray-100',
    success: 'bg-green-600 text-green-100',
    warning: 'bg-yellow-600 text-yellow-100',
    danger: 'bg-red-600 text-red-100',
    info: 'bg-blue-600 text-blue-100'
  }
  
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  )
}

export default {
  Button,
  Input,
  Select,
  Checkbox,
  LoadingSpinner,
  Card,
  Badge
}