export type ThumbnailKind = 'web_og' | 'wechat_share' | 'wechat_icon' | 'wechat_feed'

export interface ThumbnailCopy {
  brand: string
  title: string
  subtitle: string
  bullets: readonly string[]
  badge?: string
  footerLeft?: string
  footerRight?: string
}

export interface ThumbnailTheme {
  bgFrom: string
  bgTo: string
  accentFrom: string
  accentTo: string
  text: string
  muted: string
  border: string
}

export interface ThumbnailSpec {
  width: number
  height: number
  radius: number
  copy: ThumbnailCopy
  theme?: Partial<ThumbnailTheme>
  layout?: 'default' | 'centered'
}

export function escapeXml(input: string): string {
  return input
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;')
}

export function getDefaultThumbnailSpec(kind: ThumbnailKind): ThumbnailSpec {
  const baseTheme: ThumbnailTheme = {
    bgFrom: '#070A12',
    bgTo: '#0B1225',
    accentFrom: '#34D399',
    accentTo: '#3B82F6',
    text: '#FFFFFF',
    muted: 'rgba(255,255,255,0.72)',
    border: 'rgba(255,255,255,0.12)',
  }

  if (kind === 'web_og') {
    return {
      width: 1200,
      height: 660,
      radius: 36,
      theme: baseTheme,
      copy: {
        brand: 'HRD的黑匣子',
        title: 'HRD的黑匣子',
        subtitle: '对照 JD 逐条拆解差距，给出可执行改写建议',
        bullets: ['匹配评分', '改写建议', '面试话术'],
        // badge: 'DeepSeek V3',
        footerLeft: '上传简历 + JD',
        footerRight: '30 秒出报告',
      },
    }
  }

  if (kind === 'wechat_share') {
    return {
      width: 500,
      height: 400,
      radius: 28,
      theme: baseTheme,
      copy: {
        brand: 'HRD的黑匣子',
        title: 'HRD的黑匣子',
        subtitle: '打分 + 建议 + 话术',
        bullets: ['更像目标岗位', '更容易过筛', '更快拿面试'],
        // badge: 'AI',
        footerLeft: '15年HRD经验',
        footerRight: '30 秒出报告',
      },
    }
  }

  if (kind === 'wechat_feed') {
    return {
      width: 330,
      height: 600,
      radius: 24,
      theme: baseTheme,
      copy: {
        brand: 'HRD的黑匣子',
        title: 'HRD的黑匣子',
        subtitle: '打分 + 建议 + 话术',
        bullets: ['更像目标岗位', '更容易过筛', '更快拿面试'],
        // badge: 'AI',
        footerLeft: '深度分析',
        footerRight: '30 秒出报告',
      },
    }
  }

  return {
    width: 512,
    height: 512,
    radius: 120,
    theme: baseTheme,
    layout: 'centered',
    copy: {
      brand: 'HRD的黑匣子',
      title: 'HRD',
      subtitle: '黑匣子',
      bullets: [],
      // badge: 'AI',
    },
  }
}

export function buildMarketingThumbnailSvg(spec: ThumbnailSpec): string {
  const theme: ThumbnailTheme = {
    bgFrom: spec.theme?.bgFrom ?? '#070A12',
    bgTo: spec.theme?.bgTo ?? '#0B1225',
    accentFrom: spec.theme?.accentFrom ?? '#34D399',
    accentTo: spec.theme?.accentTo ?? '#3B82F6',
    text: spec.theme?.text ?? '#FFFFFF',
    muted: spec.theme?.muted ?? 'rgba(255,255,255,0.72)',
    border: spec.theme?.border ?? 'rgba(255,255,255,0.12)',
  }

  const { width, height, radius } = spec
  const isWide = width >= 800
  const isCentered = spec.layout === 'centered'
  const isTall = height > width // Detect vertical layout
  
  const pad = Math.round(width * 0.07)
  const titleSize = isCentered ? Math.round(width * 0.25) : (isWide ? 72 : Math.round(width * (isTall ? 0.14 : 0.12)))
  const subSize = isCentered ? Math.round(width * 0.12) : (isWide ? 30 : Math.round(width * (isTall ? 0.07 : 0.06)))
  const brandSize = isWide ? 22 : Math.round(width * 0.05)
  const badgeSize = isWide ? 18 : Math.round(width * 0.045)

  const brand = escapeXml(spec.copy.brand)
  const title = escapeXml(spec.copy.title)
  const subtitle = escapeXml(spec.copy.subtitle)
  const badge = spec.copy.badge ? escapeXml(spec.copy.badge) : ''
  const footerLeft = spec.copy.footerLeft ? escapeXml(spec.copy.footerLeft) : ''
  const footerRight = spec.copy.footerRight ? escapeXml(spec.copy.footerRight) : ''

  const bullets = spec.copy.bullets.slice(0, 3).map((b) => escapeXml(b))

  const leftX = isCentered ? width / 2 : pad
  const topY = pad
  const textAnchor = isCentered ? 'middle' : 'start'
  
  const titleY = isCentered ? Math.round(height * 0.45) : Math.round(pad + (isWide ? 140 : (isTall ? 120 : 96)))
  const subY = isCentered ? Math.round(height * 0.65) : titleY + Math.round(titleSize * (isTall ? 1.4 : 0.78))

  const uiX = Math.round(width * 0.58)
  const uiY = Math.round(height * 0.19)
  const uiW = Math.round(width * 0.34)
  const uiH = Math.round(height * 0.62)
  const showUi = isWide

  const bulletStartY = subY + Math.round(subSize * (isTall ? 2.5 : 1.9))
  const bulletGap = isWide ? 44 : (isTall ? 50 : 34)

  const iconR = isWide ? 16 : 14
  const bulletTextSize = isWide ? 24 : Math.round(width * (isTall ? 0.055 : 0.05))

  const footerY = height - pad + 8

  const badgeW = isWide ? 160 : (width < 400 ? 70 : 100)
  const badgeH = isWide ? 44 : 32
  const badgeR = badgeH / 2
  const badgeIconSize = isWide ? 20 : 16
  const badgeIconPad = (badgeH - badgeIconSize) / 2
  
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${title}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${theme.bgFrom}"/>
      <stop offset="100%" stop-color="${theme.bgTo}"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${theme.accentFrom}"/>
      <stop offset="100%" stop-color="${theme.accentTo}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="${theme.accentTo}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="${Math.max(10, Math.round(width * 0.02))}"/>
    </filter>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M 48 0 L 0 0 0 48" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
    </pattern>
    <clipPath id="clip">
      <rect x="0" y="0" width="${width}" height="${height}" rx="${radius}" ry="${radius}"/>
    </clipPath>
  </defs>

  <g clip-path="url(#clip)">
    <rect width="${width}" height="${height}" fill="url(#bg)"/>
    <circle cx="${isCentered ? width/2 : Math.round(width * 0.26)}" cy="${isCentered ? height/2 : Math.round(height * 0.22)}" r="${Math.round(width * 0.6)}" fill="url(#glow)" filter="url(#blur)"/>
    <rect width="${width}" height="${height}" fill="url(#grid)" opacity="0.12"/>

    ${isCentered ? `
      <!-- Center Visual for Icon -->
      <g transform="translate(${width/2}, ${height/2})">
        <rect x="-${width*0.25}" y="-${width*0.25}" width="${width*0.5}" height="${width*0.5}" rx="${width*0.05}" fill="none" stroke="url(#accent)" stroke-width="4" transform="rotate(45)" opacity="0.5"/>
        <rect x="-${width*0.2}" y="-${width*0.2}" width="${width*0.4}" height="${width*0.4}" rx="${width*0.04}" fill="rgba(255,255,255,0.05)" stroke="${theme.border}" transform="rotate(45)"/>
      </g>
    ` : ''}

    ${!isCentered ? `
    <g transform="translate(${leftX}, ${topY})">
      <g>
        <circle cx="18" cy="18" r="18" fill="url(#accent)"/>
        <text x="18" y="24" text-anchor="middle" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="14" font-weight="800" fill="#061018">H</text>
        <text x="46" y="26" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="${brandSize}" font-weight="700" fill="${theme.muted}">${brand}</text>
      </g>
    </g>` : ''}

    ${badge && !isCentered ? `
    <g transform="translate(${width - pad - badgeW}, ${pad - 6})">
      <rect x="0" y="0" width="${badgeW}" height="${badgeH}" rx="${badgeR}" fill="rgba(255,255,255,0.08)" stroke="${theme.border}"/>
      <rect x="${badgeIconPad}" y="${badgeIconPad}" width="${badgeIconSize}" height="${badgeIconSize}" rx="${badgeIconSize/2}" fill="url(#accent)"/>
      <text x="${badgeIconPad + badgeIconSize + 8}" y="${badgeH/2 + badgeSize*0.35}" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="${badgeSize}" font-weight="700" fill="${theme.text}">${badge}</text>
    </g>` : ''}

    <g>
      <text x="${leftX}" y="${titleY}" text-anchor="${textAnchor}" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="${titleSize}" font-weight="900" fill="${theme.text}" letter-spacing="-1">${title}</text>
      <text x="${leftX}" y="${subY}" text-anchor="${textAnchor}" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="${subSize}" font-weight="600" fill="${theme.muted}">${subtitle}</text>
    </g>

    ${bullets.length ? `
    <g>
      ${bullets
        .map((b, i) => {
          const y = bulletStartY + i * bulletGap
          return `
      <g transform="translate(${leftX}, ${y})">
        <circle cx="${iconR}" cy="${iconR}" r="${iconR}" fill="rgba(255,255,255,0.10)" stroke="${theme.border}"/>
        <path d="M ${Math.round(iconR * 0.72)} ${Math.round(iconR * 1.02)} L ${Math.round(iconR * 0.96)} ${Math.round(iconR * 1.26)} L ${Math.round(iconR * 1.44)} ${Math.round(iconR * 0.78)}" fill="none" stroke="url(#accent)" stroke-width="${Math.max(2.5, iconR * 0.18)}" stroke-linecap="round" stroke-linejoin="round"/>
        <text x="${iconR * 2 + 14}" y="${iconR + Math.round(bulletTextSize * 0.36)}" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="${bulletTextSize}" font-weight="800" fill="${theme.text}">${b}</text>
      </g>`
        })
        .join('')}
    </g>` : ''}

    ${showUi ? `
    <g transform="translate(${uiX}, ${uiY})">
      <rect x="0" y="0" width="${uiW}" height="${uiH}" rx="26" fill="rgba(255,255,255,0.06)" stroke="${theme.border}"/>
      <rect x="18" y="18" width="${uiW - 36}" height="44" rx="14" fill="rgba(255,255,255,0.06)" stroke="${theme.border}"/>
      <text x="36" y="48" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="16" font-weight="700" fill="rgba(255,255,255,0.72)">Analysis</text>

      <rect x="18" y="86" width="${uiW - 36}" height="${Math.round(uiH * 0.26)}" rx="18" fill="rgba(0,0,0,0.22)" stroke="${theme.border}"/>
      <rect x="36" y="110" width="${Math.round(uiW * 0.46)}" height="14" rx="7" fill="rgba(255,255,255,0.14)"/>
      <rect x="36" y="138" width="${Math.round(uiW * 0.62)}" height="10" rx="5" fill="rgba(255,255,255,0.10)"/>
      <rect x="36" y="160" width="${Math.round(uiW * 0.54)}" height="10" rx="5" fill="rgba(255,255,255,0.10)"/>

      <rect x="18" y="${Math.round(uiH * 0.48)}" width="${uiW - 36}" height="${Math.round(uiH * 0.44)}" rx="18" fill="rgba(0,0,0,0.22)" stroke="${theme.border}"/>
      <rect x="36" y="${Math.round(uiH * 0.48) + 26}" width="${Math.round(uiW * 0.36)}" height="14" rx="7" fill="rgba(255,255,255,0.14)"/>
      <rect x="36" y="${Math.round(uiH * 0.48) + 58}" width="${Math.round(uiW * 0.66)}" height="10" rx="5" fill="rgba(255,255,255,0.10)"/>
      <rect x="36" y="${Math.round(uiH * 0.48) + 80}" width="${Math.round(uiW * 0.58)}" height="10" rx="5" fill="rgba(255,255,255,0.10)"/>
      <rect x="36" y="${Math.round(uiH * 0.48) + 102}" width="${Math.round(uiW * 0.62)}" height="10" rx="5" fill="rgba(255,255,255,0.10)"/>

      <g transform="translate(${uiW - 132}, 22)">
        <rect x="0" y="0" width="114" height="34" rx="17" fill="url(#accent)" opacity="0.18" stroke="url(#accent)"/>
        <text x="57" y="23" text-anchor="middle" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="14" font-weight="800" fill="${theme.text}">Match 86%</text>
      </g>
    </g>` : ''}

    ${(footerLeft || footerRight) && !isCentered ? `
    <g>
      ${footerLeft ? `<text x="${leftX}" y="${footerY}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="${isWide ? 18 : 16}" font-weight="700" fill="rgba(255,255,255,0.55)">${footerLeft}</text>` : ''}
      ${(() => {
        if (!footerRight) return ''
        // Detect "30" to apply "Speed Mode" marketing design
        const match = footerRight.match(/^(\d+)\s*(.*)$/)
        if (match && match[1] === '30') {
           const num = match[1]
           const rest = match[2]
           const bigSize = isWide ? 48 : 36
           const smallSize = isWide ? 18 : 16
           // Estimate width to position icon to the left: (Unit Width) + (Number Width) + Padding
            // Adjusted for Sans-serif Heavy Italic font
            const offset = (rest.length * smallSize * 1.0) + (num.length * bigSize * 0.55) + 16
            
            return `
            <g transform="translate(${width - pad}, ${footerY})">
              <!-- Speed Icon (Lightning) -->
              <g transform="translate(-${offset}, -${bigSize * 0.6}) scale(${isWide?1.2:1})">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="url(#accent)" stroke="${theme.bgFrom}" stroke-width="2" stroke-linejoin="round"/>
              </g>
              <!-- Emphasized Number + Unit -->
              <text text-anchor="end" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial">
                <tspan font-size="${bigSize}" font-weight="900" font-style="italic" fill="url(#accent)" letter-spacing="-1" style="text-shadow: 0 0 30px ${theme.accentFrom}">${num}</tspan>
                <tspan font-size="${smallSize}" font-weight="700" fill="${theme.muted}" dx="4" dy="-${bigSize * 0.15}">${rest}</tspan>
              </text>
            </g>`
         }
        return `<text x="${width - pad}" y="${footerY}" text-anchor="end" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="${isWide ? 18 : 16}" font-weight="800" fill="rgba(255,255,255,0.72)">${footerRight}</text>`
      })()}
    </g>` : ''}
  </g>
</svg>
`.trim()

  return svg
}

export function toSvgDataUrl(svg: string): string {
  const encoded = encodeURIComponent(svg)
    .replaceAll('%0A', '')
    .replaceAll('%20', ' ')
    .replaceAll('%3D', '=')
    .replaceAll('%3A', ':')
    .replaceAll('%2F', '/')
    .replaceAll('%2C', ',')
    .replaceAll('%3B', ';')

  return `data:image/svg+xml;charset=utf-8,${encoded}`
}

