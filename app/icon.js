// app/icon.js
import { ImageResponse } from 'next/server'

export const runtime = 'edge'

export const size = {
  width: 32,
  height: 32,
}

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 20,
          background: 'linear-gradient(135deg, #10B981, #059669)',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          borderRadius: '6px',
          fontWeight: 'bold',
          fontFamily: 'system-ui, sans-serif',
        }}
      >
        AM
      </div>
    ),
    {
      ...size,
    }
  )
}
