import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Upload, FileText, Settings, Users, ArrowLeft, Sparkles, ChartColumn, Mail } from 'lucide-react'
import { BatchResumeParser } from './BatchResumeParser'
import { JDOptimizer } from './JDOptimizer'
import { MatchModelConfig } from './MatchModelConfig'

interface HRDashboardProps {
  onBack: () => void
}

export function HRDashboard({ onBack }: HRDashboardProps) {
  const [activeFeature, setActiveFeature] = useState<'batch' | 'jd' | 'match' | null>(null)

  if (activeFeature === 'batch') {
    return <BatchResumeParser onBack={() => setActiveFeature(null)} />
  }

  if (activeFeature === 'jd') {
    return <JDOptimizer onBack={() => setActiveFeature(null)} />
  }

  if (activeFeature === 'match') {
      return <MatchModelConfig onBack={() => setActiveFeature(null)} onSave={() => setActiveFeature(null)} />
  }

  return (
    <div className="min-h-screen bg-[#F5F5F7] p-4 md:p-8 font-sans text-[#1D1D1F]">
      <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
        
        {/* Header */}
        <header className="flex items-center justify-between pb-6 border-b border-gray-200/60">
          <div className="flex items-center gap-4">
              <div className="h-12 w-12 bg-black rounded-2xl flex items-center justify-center text-white shadow-xl shadow-black/10">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-gray-900">招聘指挥中心</h1>
                <p className="text-gray-500 font-medium">TalentOS · 开启上帝视角</p>
              </div>
          </div>
          <Button variant="outline" onClick={onBack} className="rounded-full px-6 border-gray-300 hover:bg-gray-100 hover:text-red-600 transition-all">
             退出工作台
          </Button>
        </header>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Feature 1: Batch Parser */}
          <div 
            onClick={() => setActiveFeature('batch')}
            className="rounded-3xl border border-white/50 bg-white/80 backdrop-blur-xl text-card-foreground shadow-sm p-6 space-y-4 hover:shadow-lg transition-all cursor-pointer group hover:-translate-y-1 duration-300"
          >
            <div className="p-3 bg-blue-50 rounded-xl w-fit group-hover:scale-110 transition-transform">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold group-hover:text-blue-600 transition-colors">批量简历解析</h3>
            <p className="text-gray-500 text-sm leading-relaxed">
              一键上传海量简历，AI 自动提取核心信息，生成结构化人才数据库。
            </p>
          </div>

          {/* Feature 2: JD Optimizer */}
          <div 
            onClick={() => setActiveFeature('jd')}
            className="rounded-3xl border border-white/50 bg-white/80 backdrop-blur-xl text-card-foreground shadow-sm p-6 space-y-4 hover:shadow-lg transition-all cursor-pointer group hover:-translate-y-1 duration-300"
          >
            <div className="p-3 bg-purple-50 rounded-xl w-fit group-hover:scale-110 transition-transform">
              <Sparkles className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold group-hover:text-purple-600 transition-colors">JD 智能优化</h3>
            <p className="text-gray-500 text-sm leading-relaxed">
              深度诊断职位描述，利用大数据优化关键词，提升人才匹配精准度。
            </p>
          </div>

          {/* Feature 3: Match Model */}
          <div 
            onClick={() => setActiveFeature('match')}
            className="rounded-3xl border border-white/50 bg-white/80 backdrop-blur-xl text-card-foreground shadow-sm p-6 space-y-4 hover:shadow-lg transition-all cursor-pointer group hover:-translate-y-1 duration-300"
          >
            <div className="p-3 bg-green-50 rounded-xl w-fit group-hover:scale-110 transition-transform">
              <ChartColumn className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-bold group-hover:text-green-600 transition-colors">人岗匹配模型</h3>
            <p className="text-gray-500 text-sm leading-relaxed">
              自定义权重维度（学历/经验/技能），构建企业专属的人才筛选漏斗。
            </p>
          </div>

        </div>

      </div>
    </div>
  )
}
