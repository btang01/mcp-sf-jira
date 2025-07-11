import React from 'react';
import { Brain, Loader2 } from 'lucide-react';

const ThinkingIndicator = ({ message = "Thinking", size = "sm", variant = "default" }) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  };

  const variants = {
    default: "text-blue-600 bg-blue-50 border-blue-200",
    success: "text-green-600 bg-green-50 border-green-200",
    warning: "text-yellow-600 bg-yellow-50 border-yellow-200",
    minimal: "text-gray-600"
  };

  if (variant === "minimal") {
    return (
      <div className="flex items-center space-x-2">
        <Loader2 className={`${sizeClasses[size]} animate-spin text-gray-400`} />
        <span className="text-sm text-gray-500 thinking-dots">{message}</span>
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border ${variants[variant]} transition-all duration-200`}>
      <Brain className={`${sizeClasses[size]} animate-pulse`} />
      <span className="text-sm font-medium thinking-dots">{message}</span>
    </div>
  );
};

export default ThinkingIndicator;