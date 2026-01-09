import { AlertCircle, RefreshCcw } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface ErrorDisplayProps {
  message: string
  onRetry: () => void
}

export function ErrorDisplay({ message, onRetry }: ErrorDisplayProps) {
  return (
    <div className="rounded-2xl bg-red-50 border border-red-100 p-4 animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <AlertCircle className="w-5 h-5 text-red-600" />
        </div>
        <div className="flex-1 space-y-2">
          <h3 className="text-sm font-semibold text-red-900">分析中断</h3>
          <p className="text-sm text-red-700 leading-relaxed opacity-90">
            {message || '发生未知错误，请检查网络连接或文件格式。'}
          </p>
          <div className="pt-1">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRetry}
              className="bg-white hover:bg-red-50 text-red-700 border-red-200 h-8 text-xs hover:text-red-800"
            >
              <RefreshCcw className="w-3.5 h-3.5 mr-1.5" />
              重试
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
