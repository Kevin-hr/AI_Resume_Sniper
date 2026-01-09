import { motion } from 'framer-motion'
import { User, Briefcase, ChevronRight, Check } from 'lucide-react'

interface RoleSelectorProps {
  onSelectCandidate: () => void
  onSelectHR: () => void
}

export function RoleSelector({ onSelectCandidate, onSelectHR }: RoleSelectorProps) {
  return (
    <div className="min-h-screen bg-[#070A12] flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12 space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">
            选择您的<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#34D399] to-[#3B82F6]">身份角色</span>
          </h1>
          <p className="text-gray-400 text-lg">
            系统将为您提供量身定制的功能界面与分析模型
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Candidate Card */}
          <RoleCard
            icon={<User className="w-12 h-12 text-[#34D399]" />}
            title="我是求职者"
            subtitle="CANDIDATE"
            description="针对个人简历进行深度诊断，获取改写建议与面试话术，提升过筛率。"
            features={['简历深度诊断', 'JD 匹配度分析', '面试话术生成']}
            onClick={onSelectCandidate}
            accentColor="group-hover:border-[#34D399]"
            buttonColor="bg-[#34D399] hover:bg-[#10B981] text-[#061018]"
          />

          {/* HR Card */}
          <RoleCard
            icon={<Briefcase className="w-12 h-12 text-[#3B82F6]" />}
            title="我是招聘方"
            subtitle="HR / RECRUITER"
            description="批量解析候选人简历，自动生成面试题库，优化职位描述(JD)吸引力。"
            features={['批量简历解析', '人岗匹配打分', '智能 JD 优化']}
            onClick={onSelectHR}
            accentColor="group-hover:border-[#3B82F6]"
            buttonColor="bg-[#3B82F6] hover:bg-[#2563EB] text-white"
          />
        </div>
      </div>
    </div>
  )
}

function RoleCard({ 
  icon, 
  title, 
  subtitle, 
  description, 
  features, 
  onClick,
  accentColor,
  buttonColor
}: { 
  icon: React.ReactNode
  title: string
  subtitle: string
  description: string
  features: string[]
  onClick: () => void
  accentColor: string
  buttonColor: string
}) {
  return (
    <motion.div 
      whileHover={{ y: -8 }}
      className={`group relative bg-[#0B1225] border border-gray-800 rounded-3xl p-8 cursor-pointer transition-all duration-300 ${accentColor} hover:border-opacity-50 hover:shadow-2xl`}
      onClick={onClick}
    >
      <div className="space-y-6">
        <div className="p-4 bg-gray-900/50 rounded-2xl w-fit border border-gray-800 group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white mb-1">{title}</h2>
          <p className="text-sm font-bold text-gray-500 tracking-wider">{subtitle}</p>
        </div>

        <p className="text-gray-400 leading-relaxed">
          {description}
        </p>

        <div className="space-y-3 pt-4 border-t border-gray-800">
          {features.map((feature, i) => (
            <div key={i} className="flex items-center text-gray-300">
              <Check className="w-4 h-4 mr-2 text-gray-500" />
              <span className="text-sm">{feature}</span>
            </div>
          ))}
        </div>

        <button 
          className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all mt-6 ${buttonColor}`}
        >
          进入工作台 <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </motion.div>
  )
}
