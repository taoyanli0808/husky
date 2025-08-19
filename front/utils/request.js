import axios from 'axios'
import { Message, Loading } from 'element-ui'

// 创建axios实例
const service = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 5000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 可以在这里添加请求头，如token
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers['Authorization'] = `Bearer ${token}`
    // }
    return config
  },
  error => {
    // 处理请求错误
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    // 如果返回的状态码不是200，说明请求失败
    if (res.code !== 0) {
      Message({
        message: res.message || '请求失败',
        type: 'error',
        duration: 3 * 1000
      })
      // 可以在这里处理特定错误码
      // if (res.code === 401) {
      //   // 处理未授权
      // }
      return Promise.reject(new Error(res.message || '请求失败'))
    } else {
      return res
    }
  },
  error => {
    console.error('响应错误:', error)
    Message({
      message: error.message || '服务器异常',
      type: 'error',
      duration: 3 * 1000
    })
    return Promise.reject(error)
  }
)

export default service

// API请求封装
export const request = {
  get(url, params) {
    return service.get(url, { params })
  },
  post(url, data) {
    return service.post(url, data)
  },
  put(url, data) {
    return service.put(url, data)
  },
  delete(url, params) {
    return service.delete(url, { params })
  }
}