import { useState, useRef } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ArrowLeft, Loader2, Sparkles, Copy, Check, UploadCloud, FileText, XCircle, Download } from 'lucide-react'
// import ReactMarkdown from 'react-markdown'

interface JDOptimizerProps {
  onBack: () => void
}

export function JDOptimizer({ onBack }: JDOptimizerProps) {
  const [jdText, setJdText] = useState('')
  const [jdFile, setJdFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<{ report: string } | null>(null)
  const [copied, setCopied] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
          setJdFile(e.target.files[0])
          setJdText('')
      }
  }

  const handleOptimize = async () => {
    if (!jdText.trim() && !jdFile) return
    
    setIsLoading(true)
    try {
      const formData = new FormData()
      if (jdFile) {
          formData.append('jd_file', jdFile)
      } else {
          formData.append('jd_text', jdText)
      }
      
      const response = await fetch('http://localhost:8000/optimize_jd', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) throw new Error('Optimization failed')
      
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error(error)
      // TODO: Add proper error handling UI
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleExport = () => {
      if (!result) return
      
      const blob = new Blob([result.report], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `optimized_jd_${new Date().toISOString().slice(0,10)}.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
  }

  const copyToClipboard = () => {
    if (result) {
      navigator.clipboard.writeText(result.report)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="flex items-center gap-4 pb-6 border-b border-gray-200/60">
        <Button variant="ghost" size="icon" onClick={onBack} className="rounded-full hover:bg-gray-100 h-10 w-10 text-gray-500 hover:text-black">
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-blue-600 flex items-center gap-2">
            <Sparkles className="w-6 h-6" />
            JD 智能优化
          </h1>
          <p className="text-gray-500 text-sm">大数据驱动的职位描述优化引擎</p>
        </div>
      </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
          {/* Input Section */}
          <Card className="flex flex-col p-6 space-y-4 h-full border-none shadow-sm relative">
            <h2 className="font-semibold text-lg">原始 JD</h2>
            
            {!jdFile ? (
                <textarea
                  className="flex-1 w-full p-4 bg-gray-50 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all text-sm leading-relaxed"
                  placeholder="请粘贴原始职位描述... (或者点击右下角上传 JD 文件)"
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />
            ) : (
                <div className="flex-1 w-full p-4 bg-blue-50/30 rounded-xl border-2 border-dashed border-blue-200 flex flex-col items-center justify-center relative group">
                    <FileText className="w-12 h-12 text-blue-500 mb-4 group-hover:scale-110 transition-transform" />
                    <span className="font-medium text-lg text-gray-700">{jdFile.name}</span>
                    <p className="text-sm text-blue-500 mt-2">已加载 JD 文件，准备优化</p>
                    <button 
                        onClick={() => setJdFile(null)}
                        className="absolute top-4 right-4 text-gray-400 hover:text-red-500 transition-colors"
                    >
                        <XCircle className="w-6 h-6" />
                    </button>
                </div>
            )}

            <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept=".pdf,.docx,.doc,.txt,.md"
                onChange={handleFileChange}
            />

            {!jdFile && (
                <div className="absolute bottom-24 right-8">
                     <button
                         onClick={() => fileInputRef.current?.click()}
                         className="text-sm bg-white border border-gray-200 hover:border-blue-500 hover:text-blue-600 text-gray-600 px-4 py-2 rounded-full transition-all shadow-sm flex items-center gap-2"
                     >
                         <UploadCloud className="w-4 h-4" />
                         上传文件
                     </button>
                </div>
            )}

            <Button 
              onClick={handleOptimize} 
              disabled={(!jdText.trim() && !jdFile) || isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white h-12 text-lg font-medium shadow-lg shadow-blue-500/20"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  正在深度优化...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  立即优化
                </>
              )}
            </Button>
          </Card>

          {/* Output Section */}
          <Card className="flex flex-col p-6 h-full border-none shadow-sm bg-white/80 backdrop-blur overflow-hidden">
             <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-lg">优化建议</h2>
             </div>
             
             <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
               {result ? (
                 <div className="prose prose-sm max-w-none prose-headings:font-bold prose-h2:text-blue-600 prose-p:text-gray-600">
                   <div className="flex justify-end mb-2 gap-2">
                     <Button variant="outline" size="sm" onClick={copyToClipboard} className="text-xs">
                       {copied ? <Check className="w-3 h-3 mr-1" /> : <Copy className="w-3 h-3 mr-1" />}
                       {copied ? '已复制' : '复制'}
                     </Button>
                     <Button variant="outline" size="sm" onClick={handleExport} className="text-xs">
                       <Download className="w-3 h-3 mr-1" />
                       导出 MD
                     </Button>
                   </div>
                   {/* <ReactMarkdown>{result.report}</ReactMarkdown> */}
                   <pre className="whitespace-pre-wrap font-sans">{result.report}</pre>
                 </div>
               ) : (
                 <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-4">
                   <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                     <Sparkles className="w-8 h-8 text-gray-300" />
                   </div>
                   <p>优化结果将显示在这里</p>
                 </div>
               )}
             </div>
          </Card>
        </div>
    </div>
  )
}
