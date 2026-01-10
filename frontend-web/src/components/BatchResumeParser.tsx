import { useState, useRef } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ArrowLeft, UploadCloud, FileText, Loader2, CheckCircle, AlertCircle, Download, XCircle, Send, MessageSquare } from 'lucide-react'

interface BatchResumeParserProps {
  onBack: () => void
}

interface ParseResult {
  filename: string
  status: 'success' | 'error'
  data?: any
  error?: string
}

interface MessageResult {
  candidate_id: string
  name: string
  message: string
  error?: string
}

export function BatchResumeParser({ onBack }: BatchResumeParserProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [results, setResults] = useState<ParseResult[]>([])
  const [jdText, setJdText] = useState('')
  const [jdFile, setJdFile] = useState<File | null>(null)
  const [isTranslating, setIsTranslating] = useState(false)
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([])
  const [generatedMessages, setGeneratedMessages] = useState<MessageResult[]>([])
  const [showMessages, setShowMessages] = useState(false)
  
  // Message Config
  const [messageType, setMessageType] = useState<'reject' | 'invite'>('reject')
  const [messageConfig, setMessageConfig] = useState({
      style: 'Professional',
      time: '下周二下午2点',
      interviewer: 'HR Manager',
      tips: '请携带简历'
  })

  const fileInputRef = useRef<HTMLInputElement>(null)
  const jdFileInputRef = useRef<HTMLInputElement>(null)

  const handleTranslate = async () => {
    if (!jdText.trim()) return
    setIsTranslating(true)
    try {
      const response = await fetch('http://localhost:8000/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: jdText, target_lang: "Chinese" })
      })
      const data = await response.json()
      if (data.translated_text) {
        setJdText(data.translated_text)
      }
    } catch (e) {
      console.error('Translation failed', e)
    } finally {
      setIsTranslating(false)
    }
  }

  const handleJdFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setJdFile(e.target.files[0])
      setJdText('') // Clear text if file selected
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFiles(e.target.files)
    }
  }

  const processFiles = async (files: FileList) => {
    setIsUploading(true)
    setResults([]) 
    setSelectedCandidates([])
    setGeneratedMessages([])
    
    const formData = new FormData()
    Array.from(files).forEach(file => {
      formData.append('files', file)
    })
    
    // Append JD if available
    if (jdFile) {
        formData.append('jd_file', jdFile)
    } else if (jdText.trim()) {
        formData.append('jd_text', jdText)
    }

    // Append Weights if available
    const savedWeights = localStorage.getItem('match_weights')
    if (savedWeights) {
        formData.append('weights', savedWeights)
    }

    try {
      // Choose endpoint based on JD presence
      const endpoint = (jdText.trim() || jdFile)
          ? 'http://localhost:8000/batch_analyze_match'
          : 'http://localhost:8000/batch_parse_resumes'

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      setResults(data)
      
      // Auto-select unsuitable if match
      if (jdText.trim()) {
          const unsuitable = data
            .filter((r: any) => r.status === 'success' && r.data?.status === 'Unsuitable')
            .map((r: any) => r.filename)
          // setSelectedCandidates(unsuitable) // Optional: Auto select? Maybe better to let user choose
      }

    } catch (error) {
      console.error('Batch parse error:', error)
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const generateBatchMessages = async () => {
      if (selectedCandidates.length === 0) return
      
      setIsUploading(true) // Reuse loading state
      
      try {
          const candidatesToProcess = results
            .filter(r => selectedCandidates.includes(r.filename) && r.status === 'success')
            .map(r => ({
                id: r.filename,
                name: r.data?.name || 'Candidate',
                reason: r.data?.reason || 'Profile review'
            }))
            
          const payload = {
              candidates: candidatesToProcess,
              job_info: { role: "Target Position" }, // Could extract from JD if parsed
              msg_type: messageType,
              options: messageConfig
          }
          
          const response = await fetch('http://localhost:8000/generate_messages', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
          })
          
          const data = await response.json()
          setGeneratedMessages(data)
          setShowMessages(true)
          
      } catch (e) {
          console.error(e)
      } finally {
          setIsUploading(false)
      }
  }

  const exportToCSV = () => {
    if (results.length === 0) return

    // Dynamic headers based on data
    const headers = ['Filename', 'Name', 'Score', 'Status', 'Reason', 'Email', 'Phone', 'Current Company', 'Years Exp']
    const rows = results.map(r => {
      if (r.status === 'error') return [r.filename, 'ERROR', '', '', r.error, '', '', '', '']
      
      const d = r.data || {}
      
      return [
        r.filename,
        d.name || '',
        d.score || '',
        d.status || '',
        d.reason || '',
        d.email || '',
        d.phone || '',
        d.current_company || '',
        d.years_of_experience || '',
      ].map(field => `"${String(field || '').replace(/"/g, '""')}"`)
    })

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `resume_analysis_${new Date().getTime()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="min-h-screen bg-[#F5F5F7] p-4 md:p-8 font-sans text-[#1D1D1F]">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <header className="flex items-center justify-between pb-6 border-b border-gray-200/60">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={onBack} className="text-gray-500 hover:text-black">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-purple-600 flex items-center gap-2">
                <UploadCloud className="w-6 h-6" />
                批量简历分析 & 招聘助理
              </h1>
              <p className="text-gray-500 text-sm">智能人岗匹配，一键生成反馈</p>
            </div>
          </div>
          {results.length > 0 && (
             <Button onClick={exportToCSV} variant="outline" className="flex items-center gap-2">
               <Download className="w-4 h-4" />
               导出报表
             </Button>
          )}
        </header>

        {/* 1. JD Input Section */}
        <Card className="p-6 border-none shadow-sm space-y-4">
            <h3 className="font-bold text-lg flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                第一步：输入岗位要求 (JD)
            </h3>
            <div className="relative">
                {!jdFile ? (
                    <>
                        <textarea 
                            className="w-full h-32 p-4 rounded-xl border border-gray-200 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
                            placeholder="在此粘贴 Job Description... (或者点击右下角上传 JD 文件)"
                            value={jdText}
                            onChange={(e) => setJdText(e.target.value)}
                        />
                        {jdText && (
                             <div className="absolute top-2 right-2">
                                <button
                                    onClick={handleTranslate}
                                    disabled={isTranslating}
                                    className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-2 py-1 rounded transition-colors disabled:opacity-50"
                                >
                                    {isTranslating ? '翻译中...' : '翻译为中文'}
                                </button>
                             </div>
                        )}
                    </>
                ) : (
                    <div className="w-full h-32 p-4 rounded-xl border-2 border-dashed border-blue-200 bg-blue-50/50 flex flex-col items-center justify-center relative group">
                        <FileText className="w-8 h-8 text-blue-500 mb-2 group-hover:scale-110 transition-transform" />
                        <span className="font-medium text-gray-700">{jdFile.name}</span>
                        <p className="text-xs text-blue-500 mt-1">已加载 JD 文件</p>
                        <button 
                            onClick={() => setJdFile(null)}
                            className="absolute top-2 right-2 text-gray-400 hover:text-red-500 transition-colors"
                        >
                            <XCircle className="w-5 h-5" />
                        </button>
                    </div>
                )}

                <input 
                    type="file" 
                    ref={jdFileInputRef} 
                    className="hidden" 
                    accept=".pdf,.docx,.doc,.txt,.md"
                    onChange={handleJdFileChange}
                />
                
                {!jdFile && (
                    <div className="absolute bottom-3 right-3">
                        <button
                            onClick={() => jdFileInputRef.current?.click()}
                            className="text-xs bg-white border border-gray-200 hover:border-blue-500 hover:text-blue-600 text-gray-600 px-3 py-1.5 rounded-full transition-all shadow-sm flex items-center gap-1.5"
                        >
                            <UploadCloud className="w-3 h-3" />
                            上传 JD 文件
                        </button>
                    </div>
                )}
            </div>
        </Card>

        {/* 2. Upload Section */}
        {results.length === 0 && !isUploading && (
          <Card className="p-12 border-dashed border-2 border-gray-300 bg-gray-50/50 hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => fileInputRef.current?.click()}>
            <div className="flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-16 h-16 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center">
                <UploadCloud className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">第二步：上传简历文件</h3>
                <p className="text-gray-500 mt-2">支持 PDF, DOCX, TXT (支持批量选择)</p>
              </div>
              <input 
                type="file" 
                multiple 
                className="hidden" 
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf,.docx,.txt,.doc"
              />
            </div>
          </Card>
        )}

        {/* Loading State */}
        {isUploading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <Loader2 className="w-12 h-12 text-purple-600 animate-spin" />
            <h3 className="text-lg font-medium text-gray-600">正在智能分析...</h3>
            <p className="text-sm text-gray-400">DeepSeek 正在阅读简历并与 JD 进行匹配评分</p>
          </div>
        )}

        {/* 3. Results Table & Actions */}
        {results.length > 0 && !showMessages && (
          <div className="space-y-4">
              {/* Operations Bar */}
              <div className="flex items-center justify-between bg-white p-4 rounded-xl shadow-sm">
                  <div className="flex items-center gap-4">
                      <span className="text-sm font-medium text-gray-600">已选: {selectedCandidates.length} 人</span>
                      <div className="h-6 w-px bg-gray-200"></div>
                      <select 
                        className="text-sm border-none bg-gray-50 rounded-lg p-2 focus:ring-0 cursor-pointer"
                        value={messageType}
                        onChange={(e) => setMessageType(e.target.value as any)}
                      >
                          <option value="reject">批量拒信 (Rejection)</option>
                          <option value="invite">批量邀约 (Invitation)</option>
                      </select>
                  </div>
                  <div className="flex items-center gap-2">
                      {messageType === 'reject' && (
                          <select 
                            className="text-sm border border-gray-200 rounded-lg p-2"
                            value={messageConfig.style}
                            onChange={(e) => setMessageConfig({...messageConfig, style: e.target.value})}
                          >
                              <option value="Professional">风格：专业客观</option>
                              <option value="Empathetic">风格：亲和鼓励</option>
                              <option value="Direct">风格：直接简洁</option>
                          </select>
                      )}
                      {messageType === 'invite' && (
                          <input 
                            className="text-sm border border-gray-200 rounded-lg p-2 w-48"
                            placeholder="面试时间 (如: 下周二)"
                            value={messageConfig.time}
                            onChange={(e) => setMessageConfig({...messageConfig, time: e.target.value})}
                          />
                      )}
                      <Button 
                        disabled={selectedCandidates.length === 0} 
                        onClick={generateBatchMessages}
                        className="bg-black hover:bg-gray-800 text-white"
                      >
                          <Send className="w-4 h-4 mr-2" />
                          生成话术
                      </Button>
                  </div>
              </div>

              <Card className="overflow-hidden border-none shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-4 w-4">
                            <input 
                                type="checkbox" 
                                onChange={(e) => {
                                    if (e.target.checked) {
                                        setSelectedCandidates(results.map(r => r.filename))
                                    } else {
                                        setSelectedCandidates([])
                                    }
                                }}
                                checked={selectedCandidates.length === results.length && results.length > 0}
                            />
                        </th>
                        <th className="px-6 py-4 font-medium">评分</th>
                        <th className="px-6 py-4 font-medium">状态</th>
                        <th className="px-6 py-4 font-medium">姓名/文件</th>
                        <th className="px-6 py-4 font-medium">匹配/不匹配原因</th>
                        <th className="px-6 py-4 font-medium">当前背景</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {results.map((result, index) => {
                        const d = result.data || {}
                        const isSelected = selectedCandidates.includes(result.filename)
                        return (
                          <tr key={index} className={`bg-white hover:bg-gray-50/50 transition-colors ${isSelected ? 'bg-purple-50/30' : ''}`}>
                            <td className="px-6 py-4">
                                <input 
                                    type="checkbox" 
                                    checked={isSelected}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setSelectedCandidates([...selectedCandidates, result.filename])
                                        } else {
                                            setSelectedCandidates(selectedCandidates.filter(c => c !== result.filename))
                                        }
                                    }}
                                />
                            </td>
                            <td className="px-6 py-4">
                                {d.score ? (
                                    <span className={`font-bold text-lg ${d.score >= 70 ? 'text-green-600' : 'text-orange-500'}`}>
                                        {d.score}
                                    </span>
                                ) : '-'}
                            </td>
                            <td className="px-6 py-4">
                                {d.status === 'Suitable' ? (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                        合适
                                    </span>
                                ) : d.status === 'Unsuitable' ? (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                        不合适
                                    </span>
                                ) : (
                                    <span className="text-gray-400">-</span>
                                )}
                            </td>
                            <td className="px-6 py-4 font-medium text-gray-900">
                              <div>{d.name || result.filename}</div>
                              <div className="text-xs text-gray-500">{d.phone}</div>
                            </td>
                            <td className="px-6 py-4 max-w-xs">
                                <p className="text-xs text-gray-600 leading-relaxed line-clamp-3" title={d.reason}>
                                    {d.reason || '-'}
                                </p>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-xs text-gray-900">{d.current_company}</div>
                              <div className="text-xs text-gray-500">{d.current_position}</div>
                              <div className="text-xs text-gray-400 mt-1">{d.years_of_experience ? `${d.years_of_experience}年` : ''}</div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
                 <div className="p-4 bg-gray-50 border-t flex justify-center">
                    <Button onClick={() => {setResults([]); setIsUploading(false); setJdText('')}} variant="ghost" className="text-gray-500">
                       重新开始
                    </Button>
                 </div>
              </Card>
          </div>
        )}

        {/* 4. Generated Messages View */}
        {showMessages && (
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                        <MessageSquare className="w-6 h-6 text-purple-600" />
                        生成结果 ({generatedMessages.length})
                    </h3>
                    <Button onClick={() => setShowMessages(false)} variant="outline">
                        返回列表
                    </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {generatedMessages.map((msg, idx) => (
                        <Card key={idx} className="p-6 space-y-4">
                            <div className="flex justify-between items-start">
                                <h4 className="font-bold text-gray-900">{msg.name}</h4>
                                <span className={`text-xs px-2 py-1 rounded ${messageType === 'reject' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                                    {messageType === 'reject' ? '拒信' : '邀约'}
                                </span>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-700 whitespace-pre-wrap font-mono">
                                {msg.message}
                            </div>
                            <div className="flex justify-end gap-2">
                                <Button size="sm" variant="outline" onClick={() => navigator.clipboard.writeText(msg.message)}>
                                    复制内容
                                </Button>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        )}

      </div>
    </div>
  )
}
