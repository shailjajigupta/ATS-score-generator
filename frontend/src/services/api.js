import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const api = axios.create({ baseURL: API_BASE_URL })

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { data } = error.response
      let message = data?.detail || 'Something went wrong'
      if (Array.isArray(data?.detail)) {
        message = data.detail.map((d) => d.msg).join(', ')
      }
      return Promise.reject({ message })
    }
    return Promise.reject({ message: 'Network error - is the backend running at ' + API_BASE_URL + '?' })
  }
)

/**
 * Sends the resume and JD (each as either text or a File) to the backend
 * and returns the compatibility analysis.
 */
export async function analyzeCompatibility({ resumeText, resumeFile, jdText, jdFile }) {
  const formData = new FormData()

  if (resumeFile) {
    formData.append('resume_file', resumeFile)
  } else {
    formData.append('resume_text', resumeText || '')
  }

  if (jdFile) {
    formData.append('jd_file', jdFile)
  } else {
    formData.append('jd_text', jdText || '')
  }

  const res = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}
