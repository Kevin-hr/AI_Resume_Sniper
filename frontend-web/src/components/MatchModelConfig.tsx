import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ArrowLeft, Save, Sliders, Info, RotateCcw } from 'lucide-react'

interface MatchModelConfigProps {
  onBack: () => void
  onSave: (weights: Record<string, number>) => void
  initialWeights?: Record<string, number>
}

export function MatchModelConfig({ onBack, onSave, initialWeights }: MatchModelConfigProps) {
  const [weights, setWeights] = useState({
    skills: 30,
    experience: 30,
    education: 20,
    soft_skills: 20
  })

  useEffect(() => {
    if (initialWeights) {
      setWeights(initialWeights as any)
    } else {
        const saved = localStorage.getItem('match_weights')
        if (saved) {
            try {
                setWeights(JSON.parse(saved))
            } catch(e) {}
        }
    }
  }, [initialWeights])

  const handleChange = (key: string, value: number) => {
    setWeights(prev => ({ ...prev, [key]: value }))
  }
  
  const handleSave = () => {
      localStorage.setItem('match_weights', JSON.stringify(weights))
      onSave(weights)
      onBack()
  }

  const handleReset = () => {
      setWeights({
        skills: 30,
        experience: 30,
        education: 20,
        soft_skills: 20
      })
  }

  const total = Object.values(weights).reduce((a, b) => a + b, 0)

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex items-center gap-4 pb-6 border-b border-gray-200/60">
        <Button variant="ghost" size="icon" onClick={onBack} className="rounded-full hover:bg-gray-100 h-10 w-10 text-gray-500 hover:text-black">
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Sliders className="w-6 h-6 text-blue-600" />
            人岗匹配模型配置
          </h1>
          <p className="text-gray-500 text-sm">自定义人才筛选维度的权重占比，构建企业专属评估模型</p>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-6">
            <Card className="p-8 space-y-8 shadow-sm border-gray-100">
                <div className="space-y-6">
                    {/* Skills */}
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <label className="font-medium text-gray-700">技能匹配度 (Skills)</label>
                            <span className="text-blue-600 font-bold">{weights.skills}%</span>
                        </div>
                        <input 
                            type="range" min="0" max="100" step="5"
                            value={weights.skills}
                            onChange={(e) => handleChange('skills', parseInt(e.target.value))}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <p className="text-xs text-gray-400">硬技能重合度，如编程语言、工具使用等</p>
                    </div>

                    {/* Experience */}
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <label className="font-medium text-gray-700">工作经验 (Experience)</label>
                            <span className="text-blue-600 font-bold">{weights.experience}%</span>
                        </div>
                        <input 
                            type="range" min="0" max="100" step="5"
                            value={weights.experience}
                            onChange={(e) => handleChange('experience', parseInt(e.target.value))}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                         <p className="text-xs text-gray-400">行业背景、工作年限、项目复杂度、过往职级</p>
                    </div>

                    {/* Education */}
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <label className="font-medium text-gray-700">教育背景 (Education)</label>
                            <span className="text-blue-600 font-bold">{weights.education}%</span>
                        </div>
                        <input 
                            type="range" min="0" max="100" step="5"
                            value={weights.education}
                            onChange={(e) => handleChange('education', parseInt(e.target.value))}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <p className="text-xs text-gray-400">学历门槛、毕业院校、专业对口度</p>
                    </div>

                    {/* Soft Skills */}
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <label className="font-medium text-gray-700">软素质 (Soft Skills)</label>
                            <span className="text-blue-600 font-bold">{weights.soft_skills}%</span>
                        </div>
                        <input 
                            type="range" min="0" max="100" step="5"
                            value={weights.soft_skills}
                            onChange={(e) => handleChange('soft_skills', parseInt(e.target.value))}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <p className="text-xs text-gray-400">沟通能力、领导力、抗压能力、自我驱动力</p>
                    </div>
                </div>

                <div className="pt-6 border-t border-gray-100 flex items-center justify-between">
                     <div className={`text-sm font-medium ${total === 100 ? 'text-green-600' : 'text-orange-500'}`}>
                        当前总权重: {total}% {total !== 100 && '(建议调整为 100%)'}
                     </div>
                     <Button variant="ghost" size="sm" onClick={handleReset} className="text-gray-500 hover:text-gray-900">
                        <RotateCcw className="w-4 h-4 mr-2" /> 重置默认
                     </Button>
                </div>
            </Card>
          </div>

          <div className="space-y-6">
              <Card className="p-6 bg-blue-50/50 border-blue-100">
                  <h3 className="font-semibold text-blue-900 flex items-center gap-2 mb-4">
                      <Info className="w-5 h-5" />
                      模型说明
                  </h3>
                  <div className="space-y-4 text-sm text-blue-800/80">
                      <p>
                          该模型用于批量简历解析时的人岗匹配评分。AI 将根据您设定的权重，综合分析候选人的各项素质。
                      </p>
                      <ul className="list-disc pl-4 space-y-2">
                          <li><span className="font-semibold">技术岗建议:</span> 技能 40%, 经验 30%, 教育 20%, 软素质 10%</li>
                          <li><span className="font-semibold">管理岗建议:</span> 经验 40%, 软素质 30%, 技能 20%, 教育 10%</li>
                          <li><span className="font-semibold">校招建议:</span> 教育 40%, 软素质 30%, 技能 20%, 经验 10%</li>
                      </ul>
                  </div>
              </Card>

              <Button onClick={handleSave} className="w-full h-12 text-lg bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20">
                  <Save className="w-5 h-5 mr-2" />
                  保存并应用模型
              </Button>
          </div>
      </div>
    </div>
  )
}
