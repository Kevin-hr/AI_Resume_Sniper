import { describe, expect, it } from 'vitest'
import { buildMarketingThumbnailSvg, escapeXml, getDefaultThumbnailSpec } from './thumbnail'

describe('thumbnail', () => {
  it('escapes xml characters', () => {
    expect(escapeXml(`a&b<c>d"e'f`)).toBe('a&amp;b&lt;c&gt;d&quot;e&apos;f')
  })

  it('builds web og svg with expected size and title', () => {
    const spec = getDefaultThumbnailSpec('web_og')
    const svg = buildMarketingThumbnailSvg(spec)
    expect(svg).toContain('width="1200"')
    expect(svg).toContain('height="660"') // Updated height
    expect(svg).toContain('HRD的黑匣子')
    // The "30s" logic splits the string, so we check for parts
    expect(svg).toContain('30')
    expect(svg).toContain('秒出报告')
  })

  it('builds icon svg with centered layout', () => {
    const spec = getDefaultThumbnailSpec('wechat_icon')
    const svg = buildMarketingThumbnailSvg(spec)
    expect(svg).toContain('transform="rotate(45)"') // Check for the rotated square
  })

  it('renders lightning icon and speed visual for 30s claim', () => {
    const spec = getDefaultThumbnailSpec('wechat_feed')
    const svg = buildMarketingThumbnailSvg(spec)
    // Check for "30" being emphasized (Heavy Italic)
    expect(svg).toContain('font-weight="900"')
    expect(svg).toContain('font-style="italic"')
    // Check for lightning path data (partial match is enough)
    expect(svg).toContain('d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"')
  })

  it('returns correct default spec sizes', () => {
    const web = getDefaultThumbnailSpec('web_og')
    const wechat = getDefaultThumbnailSpec('wechat_share')
    const feed = getDefaultThumbnailSpec('wechat_feed')
    const icon = getDefaultThumbnailSpec('wechat_icon')

    expect([web.width, web.height]).toEqual([1200, 660])
    expect([wechat.width, wechat.height]).toEqual([500, 400])
    expect([feed.width, feed.height]).toEqual([330, 600])
    expect([icon.width, icon.height]).toEqual([512, 512])
  })
})

