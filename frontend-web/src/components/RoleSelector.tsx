import { motion } from 'framer-motion'
import { User, Briefcase, ChevronRight, Check } from 'lucide-react'

interface RoleSelectorProps {
  onSelectCandidate: () => void
  onSelectHR: () => void
}

export function RoleSelector({ onSelectCandidate, onSelectHR }: RoleSelectorProps) {
  return (
    <div className="min-h-screen bg-[#0F172A] relative overflow-hidden flex flex-col items-center justify-center p-4">
      {/* OS Background Grid */}
      <div 
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
          maskImage: 'radial-gradient(circle at center, black, transparent 80%)'
        }}
      />
      
      {/* System Status Bar */}
      <div className="absolute top-0 left-0 w-full p-4 flex justify-between items-center text-[10px] md:text-xs text-gray-500 font-mono tracking-widest uppercase z-10 opacity-50">
        <div className="flex gap-4">
          <span>TalentOS Kernel v3.0.0</span>
          <span className="text-green-500">● System Online</span>
        </div>
        <div>
          <span>Secure Connection :: Encrypted</span>
        </div>
      </div>

      <div className="max-w-6xl w-full z-10 relative">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16 space-y-4"
        >
          <div className="inline-block mb-2 px-3 py-1 border border-gray-700 rounded-full bg-gray-900/50 backdrop-blur-sm">
            <span className="text-xs font-mono text-gray-400 tracking-[0.2em] uppercase">Operating System Loaded</span>
          </div>
          <h1 className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white via-gray-200 to-gray-500 tracking-tighter">
            TalentOS
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 font-light tracking-wide max-w-2xl mx-auto border-t border-gray-800 pt-6 mt-6">
            招聘行业的底层操作系统 · <span className="text-gray-500">The Career Operating System</span>
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-4">
          {/* Candidate Card */}
          <RoleCard
            icon={<User className="w-12 h-12 text-[#34D399]" />}
            title="我是求职者"
            subtitle="THE CAREER HACKER"
            description="别再盲目海投了。升级你的 TalentOS，用 AI 逆向工程 6 秒筛选法则，让你的简历成为系统无法忽视的信号。"
            features={['黑盒逆向诊断', 'ATS 穿透力分析', '降维打击话术']}
            onClick={onSelectCandidate}
            accentColor="border-[#34D399]/20 hover:border-[#34D399]"
            buttonColor="bg-[#34D399] hover:bg-[#10B981] text-[#061018]"
            delay={0.2}
          />

          {/* HR Card */}
          <RoleCard
            icon={<Briefcase className="w-12 h-12 text-[#3B82F6]" />}
            title="我是招聘方"
            subtitle="THE TALENT RADAR"
            description="别再“读”简历了。接入 TalentOS 招聘智脑，开启上帝视角，瞬间透视候选人底牌，只锁定 1% 的真相。"
            features={['候选人底牌透视', '上帝视角匹配', '光速批量收割']}
            onClick={onSelectHR}
            accentColor="border-[#3B82F6]/20 hover:border-[#3B82F6]"
            buttonColor="bg-[#3B82F6] hover:bg-[#2563EB] text-white"
            delay={0.4}
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
  buttonColor,
  delay
}: { 
  icon: React.ReactNode
  title: string
  subtitle: string
  description: string
  features: string[]
  onClick: () => void
  accentColor: string
  buttonColor: string
  delay: number
}) {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ y: -4, scale: 1.02 }}
      className={`group relative bg-[#0F172A]/80 backdrop-blur-md border rounded-xl p-8 cursor-pointer transition-all duration-300 ${accentColor} hover:shadow-[0_0_40px_-10px_rgba(0,0,0,0.5)] overflow-hidden`}
      onClick={onClick}
    >
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <div className="text-6xl font-black font-mono tracking-tighter text-white">
           {title === "我是求职者" ? "C-SIDE" : "B-SIDE"}
        </div>
      </div>

      <div className="space-y-6 relative z-10">
        <div className="p-4 bg-gray-900/50 rounded-lg w-fit border border-gray-800 group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>

        <div>
          <h2 className="text-3xl font-bold text-white mb-2">{title}</h2>
          <p className="text-xs font-mono font-bold text-gray-500 tracking-[0.2em]">{subtitle}</p>
        </div>

        <p className="text-gray-400 leading-relaxed text-sm">
          {description}
        </p>

        <div className="space-y-3 pt-6 border-t border-gray-800/50">
          {features.map((feature, i) => (
            <div key={i} className="flex items-center text-gray-300 group/item">
              <span className={`w-1.5 h-1.5 rounded-full mr-3 ${title === "我是求职者" ? "bg-[#34D399]" : "bg-[#3B82F6]"} group-hover/item:animate-pulse`} />
              <span className="text-sm font-medium">{feature}</span>
            </div>
          ))}
        </div>

        <button 
          className={`w-full py-4 rounded-lg font-bold text-sm uppercase tracking-wider flex items-center justify-center gap-2 transition-all mt-8 shadow-lg ${buttonColor}`}
        >
          Initialize System <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  )
}
