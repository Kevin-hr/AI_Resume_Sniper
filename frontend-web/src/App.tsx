import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { FileUpload } from '@/components/FileUpload'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Loader2, Download, ChevronRight, FileText, RefreshCw } from 'lucide-react'
import LinearPreview from '@/components/LinearPreview'
import { useAnalyzeStream } from '@/hooks/useAnalyzeStream'
import ThumbnailPreview from '@/components/ThumbnailPreview'
import { RoleSelector } from '@/components/RoleSelector'
import { HRDashboard } from '@/components/HRDashboard'
import { useUserRole } from '@/hooks/useUserRole'

import { ErrorDisplay } from '@/components/ErrorDisplay'

interface AnalysisResult {
  report: string
  score?: number
  model?: string
  tokens_used?: number
}

function App() {
  const [previewMode] = useState<'none' | 'linear' | 'thumbs'>(() => {
    const params = new URLSearchParams(window.location.search)
    const preview = params.get('preview')
    if (preview === 'linear') return 'linear'
    if (preview === 'thumbs') return 'thumbs'
    return 'none'
  })

  const { role, setCandidate, setHR, clearRole } = useUserRole()

  const [file, setFile] = useState<File | null>(null)
  const [jdText, setJdText] = useState('')
  const [jdFile, setJdFile] = useState<File | null>(null)
  const [jdInputMode, setJdInputMode] = useState<'file' | 'text'>('file')
  const [persona, setPersona] = useState('hrbp')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [validationError, setValidationError] = useState('')

  const { streamedContent, isStreaming, error, analyzeStream, reset } = useAnalyzeStream()

  const handleRetry = () => {
    setValidationError('')
    reset()
  }

  if (previewMode === 'linear') {
    return <LinearPreview />
  }
  if (previewMode === 'thumbs') {
    return <ThumbnailPreview />
  }

  // 1. Role Selection Layer
  if (!role) {
    return <RoleSelector onSelectCandidate={setCandidate} onSelectHR={setHR} />
  }

  // 2. HR Dashboard Layer
  if (role === 'hr') {
    return <HRDashboard onBack={clearRole} />
  }

  // 3. Candidate Application Layer (Existing Logic)
  const handleAnalyze = async () => {
    if (!file) return
    if (!jdText && !jdFile) {
      setValidationError('请提供职位描述（粘贴文本或上传文件）')
      return
    }

    setValidationError('')
    const formData = new FormData()
    formData.append('resume_file', file)
    if (jdFile) {
      formData.append('jd_file', jdFile)
    } else {
      formData.append('jd_text', jdText)
    }
    formData.append('persona', persona)

    setResult(null)

    await analyzeStream(formData)
  }

  const downloadReport = () => {
    const content = streamedContent || result?.report
    if (!content) return
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '简历分析报告.md'
    a.click()
  }

  const displayReport = streamedContent || result?.report
  const showResult = !!displayReport || isStreaming

  return (
    <div className="min-h-screen bg-[#F5F5F7] p-4 md:p-8 font-sans text-[#1D1D1F]">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex items-center justify-between pb-6 border-b border-gray-200/60">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">HRD的黑匣子</h1>
            <p className="text-gray-500 font-medium">15年HRD经验训练</p>
          </div>
          <Button variant="ghost" onClick={clearRole} className="rounded-full flex items-center gap-2 hover:bg-gray-200/50">
            <span className="text-sm font-medium text-gray-500">当前身份: 求职者</span>
            <div className="w-8 h-8 bg-[#34D399]/20 text-[#34D399] rounded-full overflow-hidden flex items-center justify-center">
                 <RefreshCw className="w-4 h-4" />
            </div>
          </Button>
        </header>

        <main className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Inputs */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* 1. Upload */}
            <section className="space-y-3">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-black text-white text-xs">1</span>
                上传简历
              </h2>
              <FileUpload 
                onFileSelect={setFile} 
                selectedFile={file} 
                onClear={() => {
                  setFile(null)
                  setResult(null)
                  reset()
                }} 
              />
            </section>

            {/* 2. JD */}
            <section className="space-y-3">
              <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-black text-white text-xs">2</span>
                    职位描述
                  </h2>
                  <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-xs text-gray-500 hover:text-black h-8"
                      onClick={() => setJdInputMode(prev => prev === 'file' ? 'text' : 'file')}
                  >
                      {jdInputMode === 'file' ? '切换到文本输入' : '切换到文件上传'}
                  </Button>
              </div>
              
              {jdInputMode === 'file' ? (
                  <FileUpload 
                    onFileSelect={(file) => {
                      setJdFile(file)
                      setJdText('')
                      setValidationError('')
                    }}
                    selectedFile={jdFile}
                    onClear={() => setJdFile(null)}
                    label="将 JD 拖放到此处"
                  />
              ) : (
                  <div className="relative">
                    <Card className="p-1 overflow-hidden h-[200px]">
                        <textarea 
                        className="w-full h-full p-4 resize-none border-none focus:ring-0 text-base bg-transparent focus:outline-none"
                        placeholder="在此处粘贴职位描述..."
                        value={jdText}
                        onChange={(e) => {
                          setJdText(e.target.value)
                          setJdFile(null)
                          setValidationError('')
                        }}
                        />
                    </Card>
                  </div>
              )}
            </section>

            {/* 3. Persona */}
            <section className="space-y-3">
               <h2 className="text-lg font-semibold flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-black text-white text-xs">3</span>
                诊断模式
              </h2>
              <div className="grid grid-cols-2 gap-3">
                {[
                    { id: 'hrbp', label: 'HRD 毒舌模式', desc: '严厉找茬，模拟真实面试' }, 
                    { id: 'candidate', label: '职业顾问模式', desc: '温和建议，挖掘简历亮点' }
                ].map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setPersona(p.id)}
                    className={`
                      px-4 py-3 rounded-2xl text-left transition-all duration-200 border cursor-pointer
                      ${persona === p.id 
                        ? 'bg-black text-white border-black shadow-md scale-[1.02]' 
                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'}
                    `}
                  >
                    <div className="font-bold text-sm mb-0.5">{p.label}</div>
                    <div className={`text-xs ${persona === p.id ? 'text-gray-400' : 'text-gray-400'}`}>
                        {p.desc}
                    </div>
                  </button>
                ))}
              </div>
            </section>

            <Button 
              size="lg" 
              className="w-full text-lg h-14 shadow-lg shadow-blue-500/20 mt-4" 
              disabled={!file || (!jdText && !jdFile) || isStreaming}
              onClick={handleAnalyze}
            >
              {isStreaming ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  正在分析...
                </>
              ) : (
                <>
                  开始分析 <ChevronRight className="w-5 h-5 ml-1" />
                </>
              )}
            </Button>

            {(validationError || error) && (
              <ErrorDisplay 
                message={validationError || error || ''} 
                onRetry={handleRetry} 
              />
            )}
          </div>

          {/* Right Column: Results / Preview */}
          <div className="lg:col-span-7">
            {showResult ? (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* Score Card */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="p-6 md:col-span-1 bg-gradient-to-br from-blue-500 to-blue-600 text-white border-none">
                        <p className="text-blue-100 text-sm font-medium">综合得分</p>
                        <div className="mt-2 flex items-baseline gap-1">
                            <span className="text-5xl font-bold">{result?.score || '-'}</span>
                            <span className="text-blue-200">/100</span>
                        </div>
                    </Card>
                    <Card className="p-6 md:col-span-2 flex flex-col justify-between">
                        <div className="flex justify-between items-start">
                             <div>
                                <p className="text-gray-500 text-sm font-medium">分析模型</p>
                                <p className="text-lg font-semibold mt-1">{result?.model || 'DeepSeek V3 (Streaming)'}</p>
                             </div>
                             <Button variant="outline" size="sm" onClick={downloadReport} disabled={isStreaming}>
                                {isStreaming ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                                {isStreaming ? '生成中...' : '下载报告'}
                             </Button>
                        </div>
                        <div className="mt-4">
                             <p className="text-gray-500 text-sm font-medium">消耗 Tokens</p>
                             <p className="text-gray-900 font-medium">{result?.tokens_used || '计算中...'}</p>
                        </div>
                    </Card>
                </div>

                {/* Report Content */}
                <Card className="p-8 min-h-[600px] relative">
                  {isStreaming && !displayReport && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm z-10 rounded-xl">
                        <div className="flex flex-col items-center gap-3">
                            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                            <p className="text-sm font-medium text-blue-600 animate-pulse">正在连接大脑...</p>
                        </div>
                    </div>
                  )}
                  <div className="prose prose-slate max-w-none prose-headings:font-semibold prose-a:text-blue-600">
                    <ReactMarkdown>{displayReport}</ReactMarkdown>
                    {isStreaming && (
                        <span className="inline-block w-2 h-5 bg-blue-500 ml-1 animate-pulse align-middle"></span>
                    )}
                  </div>
                </Card>
              </div>
            ) : (
              <div className="h-full min-h-[600px] rounded-3xl bg-white/50 border-2 border-dashed border-gray-200 flex flex-col items-center justify-center text-gray-400 gap-4 overflow-hidden relative">
                {file && file.type === 'application/pdf' ? (
                     <iframe 
                         src={URL.createObjectURL(file)} 
                         className="w-full h-full absolute inset-0 border-none"
                         title="Resume Preview"
                     />
                ) : (
                    <>
                        <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center">
                            <FileText className="w-10 h-10 text-gray-300" />
                        </div>
                        <p className="font-medium">分析结果和预览将显示在这里</p>
                        {file && <p className="text-sm text-gray-500">已选择: {file.name}</p>}
                    </>
                )}
              </div>
            )}
          </div>

        </main>
      </div>
    </div>
  )
}

export default App
