import { useState, useEffect } from 'react'

export type UserRole = 'candidate' | 'hr' | null

function getSafeLocalStorage():
  | Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>
  | null {
  if (typeof window === 'undefined') return null
  const storage = window.localStorage as unknown
  if (!storage || typeof storage !== 'object') return null
  const maybe = storage as Partial<Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>>
  if (
    typeof maybe.getItem !== 'function' ||
    typeof maybe.setItem !== 'function' ||
    typeof maybe.removeItem !== 'function'
  ) {
    return null
  }
  return maybe as Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>
}

export function useUserRole() {
  const [role, setRole] = useState<UserRole>(() => {
    const storage = getSafeLocalStorage()
    if (!storage) return null
    return (storage.getItem('user_role') as UserRole) || null
  })

  useEffect(() => {
    const storage = getSafeLocalStorage()
    if (!storage) return
    if (role) {
      storage.setItem('user_role', role)
    } else {
      storage.removeItem('user_role')
    }
  }, [role])

  const setCandidate = () => setRole('candidate')
  const setHR = () => setRole('hr')
  const clearRole = () => setRole(null)

  return {
    role,
    setCandidate,
    setHR,
    clearRole
  }
}
