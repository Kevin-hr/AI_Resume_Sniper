import { motion } from 'framer-motion';
import { CheckCircle, Zap, FileText, ArrowRight, Bot } from 'lucide-react';

export const LinearPreview = () => {
  return (
    <div className="min-h-screen bg-[#000000] text-white font-sans overflow-hidden selection:bg-purple-500/30">
      
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-full flex items-center justify-center">
              <Bot size={14} className="text-black" />
            </div>
            <span className="font-semibold tracking-tight">HRD's Black Box</span>
          </div>
          <div className="hidden md:flex items-center gap-6 text-sm text-gray-400">
            <span className="hover:text-white transition-colors cursor-pointer">核心功能</span>
            <span className="hover:text-white transition-colors cursor-pointer">方法论</span>
            <span className="hover:text-white transition-colors cursor-pointer">定价</span>
          </div>
          <button className="bg-white/10 hover:bg-white/20 text-white px-4 py-1.5 rounded-full text-sm font-medium transition-all border border-white/5">
            登录
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative pt-32 pb-20 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
        
        {/* Background Glows */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-purple-900/20 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-40 left-1/2 -translate-x-1/2 w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-[80px] pointer-events-none" />

        {/* Badge */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-purple-300 mb-8"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
          </span>
          v2.0 with DeepSeek V3 Support
        </motion.div>

        {/* Headline */}
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-gray-500 max-w-4xl"
        >
          揭秘 HR 筛选规则 <br className="hidden md:block" />
          开启 <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">HRD 的黑匣子</span>
        </motion.h1>

        {/* Subhead */}
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-lg md:text-xl text-gray-400 max-w-2xl mb-10 leading-relaxed"
        >
          不要盲目投递。用 15 年 HRD 的视角审视你的简历，
          <br className="hidden md:block" />
          精准匹配职位 JD，让面试邀约率提升 300%。
        </motion.p>

        {/* CTA */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex items-center gap-4"
        >
          <button className="group relative px-8 py-3 bg-white text-black rounded-full font-semibold transition-all hover:shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] hover:scale-105">
            立即开始分析
            <ArrowRight className="inline-block ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
          <button className="px-8 py-3 bg-white/5 hover:bg-white/10 text-white rounded-full font-medium transition-all border border-white/10">
            查看分析样本
          </button>
        </motion.div>
      </div>

      {/* 3D App Interface Preview */}
      <div className="relative max-w-6xl mx-auto px-6 pb-32 perspective-[2000px]">
        <motion.div 
          initial={{ opacity: 0, rotateX: 20, y: 100 }}
          animate={{ opacity: 1, rotateX: 10, y: 0 }}
          transition={{ duration: 1, delay: 0.4, type: "spring" }}
          className="relative rounded-xl border border-white/10 bg-[#0A0A0A] shadow-2xl shadow-purple-900/20 overflow-hidden transform-gpu"
          style={{ transformStyle: 'preserve-3d' }}
        >
          {/* Fake Browser Header */}
          <div className="h-12 border-b border-white/5 bg-[#111] flex items-center px-4 gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
              <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
            </div>
            <div className="mx-auto px-4 py-1 rounded-md bg-white/5 text-xs text-gray-500 font-mono">
              resume-sniper.ai/dashboard
            </div>
          </div>

          {/* App Content */}
          <div className="grid grid-cols-12 h-[600px]">
            {/* Sidebar */}
            <div className="col-span-2 border-r border-white/5 bg-[#0A0A0A] p-4 flex flex-col gap-4">
              <div className="h-8 w-24 bg-white/5 rounded animate-pulse" />
              <div className="space-y-2 mt-4">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="h-8 w-full bg-white/5 rounded-md flex items-center px-2 opacity-50 hover:opacity-100 transition-opacity">
                    <div className="w-4 h-4 rounded-full bg-white/10 mr-2" />
                  </div>
                ))}
              </div>
            </div>

            {/* Main Content */}
            <div className="col-span-7 bg-[#050505] p-8">
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h3 className="text-xl font-semibold text-white">Analysis Report</h3>
                  <p className="text-gray-500 text-sm">Product Manager - ByteDance</p>
                </div>
                <div className="px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded text-sm">
                  Match Score: 85%
                </div>
              </div>

              {/* Fake Content Blocks */}
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-medium text-gray-200">Key Qualifications Met</span>
                  </div>
                  <div className="space-y-2">
                    <div className="h-2 w-3/4 bg-white/10 rounded" />
                    <div className="h-2 w-1/2 bg-white/10 rounded" />
                  </div>
                </div>
                <div className="p-4 rounded-lg bg-white/5 border border-white/5">
                   <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    <span className="text-sm font-medium text-gray-200">Suggested Improvements</span>
                  </div>
                  <div className="space-y-2">
                    <div className="h-2 w-full bg-white/10 rounded" />
                    <div className="h-2 w-5/6 bg-white/10 rounded" />
                    <div className="h-2 w-4/5 bg-white/10 rounded" />
                  </div>
                </div>
              </div>
            </div>

            {/* Right Panel */}
            <div className="col-span-3 border-l border-white/5 bg-[#0A0A0A] p-4">
               <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">AI Insights</div>
               <div className="space-y-3">
                 <div className="p-3 rounded bg-blue-500/10 border border-blue-500/20">
                   <div className="h-2 w-12 bg-blue-500/40 rounded mb-2" />
                   <div className="h-16 w-full bg-blue-500/10 rounded" />
                 </div>
                  <div className="p-3 rounded bg-purple-500/10 border border-purple-500/20">
                   <div className="h-2 w-12 bg-purple-500/40 rounded mb-2" />
                   <div className="h-16 w-full bg-purple-500/10 rounded" />
                 </div>
               </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* WeChat Mini Program Cover Preview Section */}
      <div className="max-w-7xl mx-auto px-6 py-20 border-t border-white/10">
        <h2 className="text-2xl font-bold mb-10 text-center">WeChat Mini Program Cover</h2>
        <div className="flex justify-center">
          {/* The Card */}
          <div className="relative w-[375px] h-[300px] bg-gradient-to-br from-[#1a1a1a] to-black border border-white/10 rounded-lg overflow-hidden flex flex-col items-center justify-center p-8 shadow-2xl">
            {/* Abstract Shape */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-emerald-500 to-blue-600 blur-[60px] opacity-40" />
            
            {/* Icon */}
            <div className="relative z-10 w-16 h-16 bg-gradient-to-br from-white to-gray-400 rounded-2xl flex items-center justify-center mb-6 shadow-lg rotate-3 hover:rotate-6 transition-transform">
               <FileText className="text-black w-8 h-8" />
               <div className="absolute -bottom-2 -right-2 bg-emerald-500 text-black text-[10px] font-bold px-1.5 py-0.5 rounded">AI</div>
            </div>

            {/* Text */}
            <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">HRD的黑匣子</h3>
            <p className="text-gray-400 text-sm text-center">
              DeepSeek 深度驱动 <br/>
              一键优化简历，精准匹配职位
            </p>

            {/* Decorative Grid */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none" />
          </div>
        </div>
      </div>

    </div>
  );
};

export default LinearPreview;
