import { useEffect, useRef } from 'react'

type KeyHandler = () => void

export function useKeyboard(handlers: Record<string, KeyHandler>) {
  // Use a ref so the effect never needs to re-run, but always calls latest handlers
  const ref = useRef(handlers)
  ref.current = handlers

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      // Ignore when typing inside inputs
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
      // Ignore modified shortcuts (browser shortcuts)
      if (e.ctrlKey || e.metaKey || e.altKey) return
      const fn = ref.current[e.key]
      if (fn) {
        e.preventDefault()
        fn()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, []) // intentionally empty — ref stays current
}
