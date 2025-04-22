import { NextConfig } from 'next'

const config: NextConfig = {
  rewrites: async () => {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/py/hello',
          destination: 'http://127.0.0.1:8000/hello'
        },
        {
          source: '/api/py/birth-chart',
          destination: 'http://127.0.0.1:8001/hello'  // Using port 8001 for birth-chart
        }
      ]
    }
    
    return [
      {
        source: '/api/py/hello',
        destination: '/api/hello/index.py'
      },
      {
        source: '/api/py/birth-chart',
        destination: '/api/birth-chart/index.py'
      }
    ]
  }
}

export default config
