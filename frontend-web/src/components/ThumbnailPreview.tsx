import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import {
  buildMarketingThumbnailSvg,
  getDefaultThumbnailSpec,
  toSvgDataUrl,
  type ThumbnailKind,
} from '@/lib/thumbnail'

type RenderTarget = { kind: ThumbnailKind; title: string; fileBase: string }

function downloadBlob(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function svgToPngBlob(svg: string, width: number, height: number, scale: number) {
  const svgBlob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
  const svgUrl = URL.createObjectURL(svgBlob)

  try {
    const img = new Image()
    img.decoding = 'async'
    img.src = svgUrl
    await img.decode()

    const canvas = document.createElement('canvas')
    canvas.width = Math.round(width * scale)
    canvas.height = Math.round(height * scale)

    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('canvas context not available')

    ctx.setTransform(scale, 0, 0, scale, 0, 0)
    ctx.clearRect(0, 0, width, height)
    ctx.drawImage(img, 0, 0, width, height)

    const pngBlob: Blob | null = await new Promise((resolve) =>
      canvas.toBlob((b) => resolve(b), 'image/png')
    )

    if (!pngBlob) throw new Error('png export failed')
    return pngBlob
  } finally {
    URL.revokeObjectURL(svgUrl)
  }
}

export default function ThumbnailPreview() {
  const [exportScale, setExportScale] = useState(2)
  const targets: RenderTarget[] = useMemo(
    () => [
      {
        kind: 'web_og',
        title: 'Web Open Graph (1200x660)',
        fileBase: 'og-image',
      },
      {
        kind: 'wechat_share',
        title: '微信分享卡片 (500x400)',
        fileBase: 'wechat-share',
      },
      {
        kind: 'wechat_feed',
        title: '微信信息流/搜索 (330x600)',
        fileBase: 'wechat-feed',
      },
      {
        kind: 'wechat_icon',
        title: '小程序图标 (512x512)',
        fileBase: 'wechat-icon',
      },
    ],
    []
  )

  const rendered = useMemo(() => {
    return targets.map((t) => {
      const spec = getDefaultThumbnailSpec(t.kind)
      const svg = buildMarketingThumbnailSvg(spec)
      const dataUrl = toSvgDataUrl(svg)
      return { ...t, spec, svg, dataUrl }
    })
  }, [targets])

  return (
    <div className="min-h-screen bg-[#F5F5F7] p-4 md:p-8 font-sans text-[#1D1D1F]">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="flex items-center justify-between pb-4 border-b border-gray-200/60">
          <div className="space-y-1">
            <h1 className="text-2xl font-bold tracking-tight">应用缩略图预览</h1>
            <p className="text-gray-500 font-medium">Web / 微信小程序（SVG 可直接导出）</p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={exportScale === 1 ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setExportScale(1)}
            >
              PNG 1x
            </Button>
            <Button
              variant={exportScale === 2 ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setExportScale(2)}
            >
              PNG 2x
            </Button>
            <Button
              variant={exportScale === 3 ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setExportScale(3)}
            >
              PNG 3x
            </Button>
          </div>
        </header>

        <div className="space-y-6">
          {rendered.map((r) => (
            <Card key={r.kind} className="p-5">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="space-y-1">
                  <div className="text-lg font-semibold">{r.title}</div>
                  <div className="text-sm text-gray-500">
                    {r.spec.width}×{r.spec.height} · SVG + PNG
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      downloadBlob(`${r.fileBase}.svg`, new Blob([r.svg], { type: 'image/svg+xml' }))
                    }
                  >
                    下载 SVG
                  </Button>
                  <Button
                    size="sm"
                    onClick={async () => {
                      const png = await svgToPngBlob(r.svg, r.spec.width, r.spec.height, exportScale)
                      downloadBlob(`${r.fileBase}@${exportScale}x.png`, png)
                    }}
                  >
                    下载 PNG
                  </Button>
                </div>
              </div>

              <div className="mt-4 bg-white rounded-2xl p-3 border border-gray-200/60 overflow-auto">
                <div
                  className="mx-auto"
                  style={{
                    width: Math.min(r.spec.width, 980),
                  }}
                >
                  <img
                    src={r.dataUrl}
                    width={r.spec.width}
                    height={r.spec.height}
                    className="w-full h-auto block rounded-xl"
                    alt={r.title}
                    loading="lazy"
                  />
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
