import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ArrowLeft, BarChart3, Users, FileSearch } from 'lucide-react'
import type { ReactNode } from 'react'

interface HRDashboardProps {
  onBack: () => void
}

export function HRDashboard({ onBack }: HRDashboardProps) {
  return (
    <div className="min-h-screen bg-[#F5F5F7] p-4 md:p-8 font-sans text-[#1D1D1F]">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex items-center justify-between pb-6 border-b border-gray-200/60">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={onBack} className="text-gray-500 hover:text-black">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="space-y-1">
              <h1 className="text-3xl font-bold tracking-tight text-blue-600">HRD 智库</h1>
              <p className="text-gray-500 font-medium">B端 招聘效能提升工作台</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
             <div className="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-bold">
               企业版 PRO
             </div>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <DashboardCard 
            icon={<FileSearch className="w-8 h-8 text-blue-600" />}
            title="JD 智能优化"
            desc="上传现有 JD，利用大数据分析优化关键词，提升候选人投递精准度。"
            status="Coming Soon"
          />
          <DashboardCard 
            icon={<Users className="w-8 h-8 text-purple-600" />}
            title="批量简历解析"
            desc="一键上传整个文件夹的简历，自动提取核心字段并生成对比报表。"
            status="Coming Soon"
          />
          <DashboardCard 
            icon={<BarChart3 className="w-8 h-8 text-green-600" />}
            title="人岗匹配模型"
            desc="自定义权重维度（学历/经验/技能），构建企业专属的人才筛选漏斗。"
            status="Coming Soon"
          />
        </div>

        <div className="bg-white p-12 rounded-3xl border border-gray-200 text-center space-y-6">
           <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
             <span className="text-4xl">🚀</span>
           </div>
           <h2 className="text-2xl font-bold">HR 功能模块正在极速构建中</h2>
           <p className="text-gray-500 max-w-lg mx-auto">
             我们的最强大脑团队正在为 HR 角色开发专属的 B 端功能。
             目前请先体验“求职者”视角的简历诊断功能，了解我们的核心分析能力。
           </p>
           <Button onClick={onBack} className="bg-[#1D1D1F] text-white hover:bg-black px-8">
             返回并体验求职者功能
           </Button>
        </div>

      </div>
    </div>
  )
}

interface DashboardCardProps {
  icon: ReactNode
  title: string
  desc: string
  status: string
}

function DashboardCard({ icon, title, desc, status }: DashboardCardProps) {
  return (
    <Card className="p-6 space-y-4 hover:shadow-lg transition-shadow relative overflow-hidden group">
      <div className="absolute top-3 right-3 text-xs font-bold text-gray-300 border border-gray-200 px-2 py-1 rounded">
        {status}
      </div>
      <div className="p-3 bg-gray-50 rounded-xl w-fit group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-xl font-bold">{title}</h3>
      <p className="text-gray-500 text-sm leading-relaxed">
        {desc}
      </p>
    </Card>
  )
}
