/**
 * 日期时间工具函数
 */

export function formatDate(date, format = 'datetime') {
  if (!date) return '未知'
  
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '无效日期'
  
  if (format === 'relative') {
    return formatRelativeTime(d)
  }
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')
  
  switch (format) {
    case 'date':
      return `${year}-${month}-${day}`
    case 'time':
      return `${hour}:${minute}:${second}`
    case 'datetime':
    default:
      return `${year}-${month}-${day} ${hour}:${minute}:${second}`
  }
}

export function formatRelativeTime(date) {
  if (!date) return '从未'
  
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '无效日期'
  
  const now = new Date()
  const diffMs = now - d
  const diffSeconds = Math.floor(diffMs / 1000)
  
  if (diffSeconds < 0) return '刚刚'
  if (diffSeconds < 60) return `${diffSeconds}秒前`
  
  const diffMinutes = Math.floor(diffSeconds / 60)
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours}小时前`
  
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 30) return `${diffDays}天前`
  
  const diffMonths = Math.floor(diffDays / 30)
  if (diffMonths < 12) return `${diffMonths}个月前`
  
  const diffYears = Math.floor(diffMonths / 12)
  return `${diffYears}年前`
}

export function formatDuration(ms) {
  if (!ms || ms < 0) return '0秒'
  
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}秒`
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes < 60) {
    return remainingSeconds > 0 
      ? `${minutes}分${remainingSeconds}秒`
      : `${minutes}分钟`
  }
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (hours < 24) {
    return remainingMinutes > 0
      ? `${hours}小时${remainingMinutes}分钟`
      : `${hours}小时`
  }
  
  const days = Math.floor(hours / 24)
  const remainingHours = hours % 24
  
  return remainingHours > 0
    ? `${days}天${remainingHours}小时`
    : `${days}天`
}
