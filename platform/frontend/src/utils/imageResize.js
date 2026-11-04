/**
 * Resize a raster image in the browser before sending it to the API.
 *
 * Logos are shown small, so a 512px longest edge is plenty even on high-DPI
 * displays. WebP keeps transparency and makes the base64 payload much smaller
 * than PNG for photographic or gradient logos.
 */
export function resizeImageFile(file, {
  maxDimension = 512,
  quality = 0.88,
} = {}) {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('No image selected'))
      return
    }
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('Could not read that image'))
    reader.onload = () => {
      const image = new Image()
      image.onerror = () => reject(new Error('Could not decode that image'))
      image.onload = () => {
        const scale = Math.min(
          1,
          maxDimension / Math.max(image.width, image.height)
        )
        const width = Math.max(1, Math.round(image.width * scale))
        const height = Math.max(1, Math.round(image.height * scale))
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const context = canvas.getContext('2d')
        context.clearRect(0, 0, width, height)
        context.drawImage(image, 0, 0, width, height)
        resolve(canvas.toDataURL('image/webp', quality))
      }
      image.src = reader.result
    }
    reader.readAsDataURL(file)
  })
}
