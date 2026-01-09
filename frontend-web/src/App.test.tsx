import { render, screen } from '@testing-library/react'
import App from './App'
import { describe, it, expect } from 'vitest'

describe('App', () => {
  it('renders the main title', () => {
    localStorage.setItem('user_role', 'candidate')
    render(<App />)
    expect(screen.getByText('HRD的黑匣子')).toBeInTheDocument()
  })
})
